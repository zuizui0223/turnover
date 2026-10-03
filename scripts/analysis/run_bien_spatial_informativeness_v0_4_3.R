#!/usr/bin/env Rscript
suppressPackageStartupMessages({
  library(RPostgreSQL)
  library(DBI)
  library(jsonlite)
})

args <- commandArgs(trailingOnly=TRUE)
getarg <- function(flag){
  i <- match(flag,args)
  if(is.na(i) || i==length(args)) stop(paste("missing",flag))
  args[[i+1]]
}
family <- getarg("--family")
trait_name <- getarg("--trait")
semantic_class <- getarg("--class")
system_id <- getarg("--id")
out_path <- getarg("--out")
dir.create(dirname(out_path),recursive=TRUE,showWarnings=FALSE)

root <- normalizePath(".")
design <- fromJSON(file.path(root,"data","bien_informativeness_design_v0_4.json"),simplifyVector=FALSE)
exec <- fromJSON(file.path(root,"data","bien_informativeness_execution_v0_4_2.json"),simplifyVector=FALSE)
sp_exec <- fromJSON(file.path(root,"data","bien_spatial_informativeness_execution_v0_4_3.json"),simplifyVector=FALSE)

tem <- read.csv(file.path(root,"results","bien_temporal_informativeness_v0_4_2","temporal_informativeness.csv"),stringsAsFactors=FALSE,check.names=FALSE)
tflag <- tolower(trimws(as.character(tem$system_temporal_pass))) %in% c("true","t","1")
trow <- tem[tflag & tem$family==family & tem$trait_name==trait_name,,drop=FALSE]
if(nrow(trow)!=1) stop("system is not a unique temporal-informativeness PASS candidate")
if(as.character(trow$semantic_class[[1]])!=semantic_class) stop("semantic class mismatch")

sv <- read.csv(file.path(root,"results","bien_trait_state_validity_v0_3_3","state_validity.csv"),stringsAsFactors=FALSE,check.names=FALSE)
sflag <- tolower(trimws(as.character(sv$semantic_pass))) %in% c("true","t","1")
srow <- sv[sflag & sv$family==family & sv$trait_name==trait_name,,drop=FALSE]
if(nrow(srow)!=1) stop("system is not a unique semantic PASS candidate")
expected_spatial_species <- as.integer(srow$spatial_qualifying_species[[1]])
if(expected_spatial_species<8) stop("semantic PASS table has fewer than 8 spatial species")

rbien_dir <- Sys.getenv("RBIEN_SOURCE_DIR",unset="build/RBIEN")
source(file.path(rbien_dir,"R","internals.R"))
source(file.path(rbien_dir,"R","BIEN_sql.R"))
source(file.path(rbien_dir,"R","BIEN.R"))
ver <- BIEN_metadata_database_version()
observed_version <- if(is.data.frame(ver)&&nrow(ver)) as.character(ver$db_version[[1]]) else NA_character_
if(!identical(observed_version,"4.2.8")) stop("BIEN patch changed before spatial informativeness")

esc <- function(x) gsub("'","''",x,fixed=TRUE)
famq <- esc(family); trq <- esc(trait_name)
R_earth <- 6371008.8
std <- 30*pi/180
cell <- 25000

if(semantic_class=="continuous_scalar"){
  sql <- sprintf("
    WITH base AS (
      SELECT scrubbed_species_binomial AS species,
             latitude::double precision AS lat,
             longitude::double precision AS lon,
             CASE WHEN trait_value::text ~ '^[[:space:]]*[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)([eE][+-]?[0-9]+)?[[:space:]]*$'
                  THEN trait_value::numeric ELSE NULL END AS value_num
      FROM agg_traits
      WHERE scrubbed_family='%s' AND trait_name='%s'
        AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
        AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
        AND unit IS NOT NULL AND trim(unit::text)<>''
        AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
        AND is_geovalid=1
        AND (is_centroid IS NULL OR is_centroid=0)
        AND (georef_protocol IS NULL OR georef_protocol<>'county centroid')
        AND latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180
    ), tagged AS (
      SELECT *,
        floor((%f*radians(lon)*cos(%f))/%f)::bigint AS cell_x,
        floor((%f*sin(radians(lat))/cos(%f))/%f)::bigint AS cell_y
      FROM base WHERE value_num IS NOT NULL
    ), qual AS (
      SELECT species
      FROM tagged
      GROUP BY species
      HAVING count(*)>=20
         AND count(DISTINCT (cell_x::text||':'||cell_y::text))>=5
         AND count(DISTINCT value_num)>=2
    )
    SELECT t.species,t.lat,t.lon
    FROM tagged t JOIN qual q USING(species)
    ORDER BY t.species,t.lat,t.lon;
  ",famq,trq,R_earth,std,cell,R_earth,std,cell)
} else if(semantic_class=="nominal_categorical"){
  sql <- sprintf("
    WITH base AS (
      SELECT scrubbed_species_binomial AS species,
             latitude::double precision AS lat,
             longitude::double precision AS lon,
             trait_value::text AS value_text
      FROM agg_traits
      WHERE scrubbed_family='%s' AND trait_name='%s'
        AND scrubbed_species_binomial IS NOT NULL AND trim(scrubbed_species_binomial)<>''
        AND trait_value IS NOT NULL AND trim(trait_value::text)<>''
        AND (unit IS NULL OR trim(unit::text)='')
        AND (is_cultivated_observation=0 OR is_cultivated_observation IS NULL)
        AND is_geovalid=1
        AND (is_centroid IS NULL OR is_centroid=0)
        AND (georef_protocol IS NULL OR georef_protocol<>'county centroid')
        AND latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180
    ), tagged AS (
      SELECT *,
        floor((%f*radians(lon)*cos(%f))/%f)::bigint AS cell_x,
        floor((%f*sin(radians(lat))/cos(%f))/%f)::bigint AS cell_y
      FROM base
    ), qual AS (
      SELECT species
      FROM tagged
      GROUP BY species
      HAVING count(*)>=20
         AND count(DISTINCT (cell_x::text||':'||cell_y::text))>=5
         AND count(DISTINCT value_text)>=2
    )
    SELECT t.species,t.lat,t.lon
    FROM tagged t JOIN qual q USING(species)
    ORDER BY t.species,t.lat,t.lon;
  ",famq,trq,R_earth,std,cell,R_earth,std,cell)
} else stop("unsupported semantic class")

geo <- .BIEN_sql(sql)
if(!is.data.frame(geo) || !all(c("species","lat","lon") %in% names(geo))) stop("spatial geometry query failed")
geo$species <- as.character(geo$species)
species_ids <- unique(geo$species)
if(length(species_ids)!=expected_spatial_species)
  stop(paste("spatial species count disagrees with frozen semantic gate",length(species_ids),expected_spatial_species))
if(length(species_ids)<8) stop("fewer than 8 spatial species after reconstruction")

fnv1a32_unsigned <- function(key){
  h <- 2166136261
  bytes <- as.integer(charToRaw(enc2utf8(key)))
  for(b in bytes){
    low8 <- h %% 256
    h <- h - low8 + bitwXor(as.integer(low8),as.integer(b))
    lo <- h %% 65536
    hi <- floor(h/65536)
    prodlo <- lo*403
    newlo <- prodlo %% 65536
    carry <- floor(prodlo/65536)
    newhi <- (carry + lo*256 + hi*403) %% 65536
    h <- newlo + newhi*65536
  }
  h
}
if(fnv1a32_unsigned("") != 2166136261 ||
   fnv1a32_unsigned("a") != 3826002220 ||
   fnv1a32_unsigned("foobar") != 3214735720) stop("FNV self-test failed")
fnv_seed <- function(key) as.integer((fnv1a32_unsigned(key) %% 2147483646)+1)

great_circle_matrix <- function(lat,lon){
  phi <- lat*pi/180
  lam <- lon*pi/180
  C <- outer(sin(phi),sin(phi),"*") + outer(cos(phi),cos(phi),"*") * cos(outer(lam,lam,"-"))
  C <- pmin(1,pmax(-1,C))
  R_earth * acos(C)
}

expanded_median_positive <- function(v,w){
  keep <- is.finite(v) & v>0 & w>0
  v <- v[keep]; w <- w[keep]
  if(!length(v)) stop("no positive spatial distances")
  o <- order(v); v<-v[o]; w<-w[o]
  cw <- cumsum(w); W <- sum(w)
  kth <- function(k) v[which(cw>=k)[1]]
  if(W %% 2 == 1) kth((W+1)/2) else (kth(W/2)+kth(W/2+1))/2
}

weighted_midrank <- function(v,w){
  if(length(v)!=length(w) || !length(v)) stop("bad weighted rank input")
  o <- order(v,seq_along(v))
  vo <- v[o]; wo <- w[o]
  starts <- c(TRUE,vo[-1]!=vo[-length(vo)])
  grp <- cumsum(starts)
  gw <- as.numeric(rowsum(wo,grp,reorder=FALSE)[,1])
  before <- c(0,cumsum(gw)[-length(gw)])
  gr <- before + (gw+1)/2
  out <- numeric(length(v)); out[o] <- gr[grp]
  out
}

prepare_species_geometry <- function(df){
  if(nrow(df)<20) stop("species below 20 records")
  keep <- is.finite(df$lat) & is.finite(df$lon) &
          df$lat>=-90 & df$lat<=90 & df$lon>=-180 & df$lon<=180
  df <- df[keep,,drop=FALSE]
  if(nrow(df)<20) stop("species below 20 finite coordinate records")
  ord <- order(df$lat,df$lon,method="radix")
  lat <- df$lat[ord]; lon <- df$lon[ord]
  starts <- c(TRUE, lat[-1]!=lat[-length(lat)] | lon[-1]!=lon[-length(lon)])
  grp <- cumsum(starts)
  nodes <- data.frame(lat=lat[starts],lon=lon[starts])
  mult <- as.numeric(tabulate(grp,nbins=nrow(nodes)))
  if(any(!is.finite(mult)) || any(mult<1)) stop("invalid exact-coordinate multiplicities")
  n <- nrow(nodes)
  if(n<2) stop("fewer than 2 unique spatial nodes")
  D <- great_circle_matrix(nodes$lat,nodes$lon)
  ij <- which(lower.tri(D),arr.ind=TRUE)
  pi <- ij[,1]; pj <- ij[,2]
  pd <- D[ij]
  pw <- as.numeric(mult[pi]) * as.numeric(mult[pj])
  within <- which(mult>=2)
  if(length(within)){
    pi <- c(pi,within); pj <- c(pj,within)
    pd <- c(pd,rep(0,length(within)))
    pw <- c(pw,as.numeric(mult[within])*(as.numeric(mult[within])-1)/2)
  }
  if(any(!is.finite(pw)) || any(pw<=0)) stop("invalid expanded pair multiplicity weights")
  N <- sum(mult)
  M_expected <- N*(N-1)/2
  M <- sum(pw)
  if(!is.finite(M) || M<1) stop("no finite expanded record-pair count")
  if(abs(M-M_expected) > max(1e-8,1e-12*M_expected))
    stop(paste("expanded pair-count invariant failed",M,M_expected))
  med <- expanded_median_positive(pd,pw)
  rx <- weighted_midrank(pd,pw)
  mx <- (M+1)/2
  sxx <- sum(pw*(rx-mx)^2)
  if(!is.finite(sxx) || sxx<=0) stop("zero spatial separation rank variance")
  list(D=D,pi=pi,pj=pj,pd=pd,pw=pw,rx=rx,mx=mx,sxx=sxx,M=M,med=med,
       n_nodes=n,n_records=N,species=df$species[[1]])
}

geoms <- lapply(species_ids,function(sp) prepare_species_geometry(geo[geo$species==sp,c("species","lat","lon"),drop=FALSE]))
rm(geo); gc(FALSE)

make_Z <- function(g,reps,phase){
  set.seed(fnv_seed(paste(20260930,family,trait_name,"spatial",g$species,phase,sep="|")))
  matrix(rnorm(g$n_nodes*reps),nrow=g$n_nodes,ncol=reps)
}

simulate_states <- function(g,lambda,Z){
  scale <- lambda*g$med
  if(!is.finite(scale) || scale<=0) return(NULL)
  K <- exp(-g$D/scale)
  K <- (K+t(K))/2
  diag(K) <- 1
  L <- tryCatch(t(chol(K)),error=function(e) NULL)
  if(is.null(L)) return(NULL)
  L %*% Z
}

continuous_effects <- function(states,g){
  if(is.null(states)) return(rep(NA_real_,ncol(states)))
  reps <- ncol(states); out <- rep(NA_real_,reps)
  for(r in seq_len(reps)){
    st <- states[,r]
    y <- abs(st[g$pi]-st[g$pj])
    ry <- weighted_midrank(y,g$pw)
    my <- (g$M+1)/2
    syy <- sum(g$pw*(ry-my)^2)
    if(!is.finite(syy) || syy<=0) next
    out[r] <- sum(g$pw*(g$rx-g$mx)*(ry-my))/sqrt(g$sxx*syy)
  }
  out
}

binary_effects <- function(states,g){
  reps <- ncol(states); out <- rep(NA_real_,reps)
  G <- states>0
  for(r in seq_len(reps)){
    mismatch <- G[g$pi,r] != G[g$pj,r]
    Kmis <- sum(g$pw[mismatch])
    if(Kmis<=0 || Kmis>=g$M) next
    cross_sum <- sum(g$pw[mismatch]*g$rx[mismatch])
    den <- sqrt(g$sxx*Kmis*(g$M-Kmis)/g$M)
    if(is.finite(den) && den>0) out[r] <- (cross_sum-Kmis*g$mx)/den
  }
  out
}

species_effects <- function(g,cls,lambda,reps,phase){
  Z <- make_Z(g,reps,phase)
  states <- simulate_states(g,lambda,Z)
  if(is.null(states)) return(rep(NA_real_,reps))
  if(cls=="continuous_scalar") continuous_effects(states,g) else binary_effects(states,g)
}

family_effects <- function(lambda,reps,phase){
  mat <- matrix(NA_real_,nrow=length(geoms),ncol=reps)
  for(i in seq_along(geoms)) mat[i,] <- species_effects(geoms[[i]],semantic_class,lambda,reps,phase)
  apply(mat,2,function(x){
    good <- is.finite(x)
    if(sum(good)<8) NA_real_ else median(x[good])
  })
}

pilot_stats <- function(effects){
  good <- is.finite(effects)
  list(median=if(any(good)) median(effects[good]) else NA_real_,valid_fraction=mean(good))
}

calibrate <- function(){
  target <- as.numeric(design$canonical_effect$benchmark_delta_rho)
  tol <- as.numeric(design$continuous_scalar_generator$calibration$tolerance_delta_rho)
  minvf <- as.numeric(exec$lambda_search$pilot_valid_fraction_min)
  reps <- as.integer(exec$lambda_search$pilot_replicates_per_value)
  grid <- as.numeric(unlist(exec$lambda_search$lambda_values))
  meds <- rep(NA_real_,length(grid)); vfs <- rep(0,length(grid))
  for(i in seq_along(grid)){
    stt <- pilot_stats(family_effects(grid[i],reps,"pilot"))
    meds[i] <- stt$median; vfs[i] <- stt$valid_fraction
  }
  good <- is.finite(meds) & vfs>=minvf
  diag <- lapply(seq_along(grid),function(i)list(lambda=grid[i],median_effect=meds[i],valid_fraction=vfs[i]))
  exact <- which(good & abs(meds-target)<=tol)
  if(length(exact)){
    i<-exact[1]; return(list(ok=TRUE,lambda=grid[i],pilot_median=meds[i],pilot_valid_fraction=vfs[i],grid=diag,bisection_steps=0))
  }
  bracket <- NA_integer_
  for(i in seq_len(length(grid)-1)){
    if(good[i] && good[i+1] && (meds[i]-target)*(meds[i+1]-target)<=0){ bracket<-i; break }
  }
  if(is.na(bracket)) return(list(ok=FALSE,reason="CALIBRATION_NO_BRACKET",grid=diag))
  lo<-grid[bracket]; hi<-grid[bracket+1]; mlo<-meds[bracket]
  maxstep <- as.integer(design$continuous_scalar_generator$calibration$max_bisection_steps)
  for(step in seq_len(maxstep)){
    mid <- exp((log(lo)+log(hi))/2)
    stt <- pilot_stats(family_effects(mid,reps,"pilot"))
    if(!is.finite(stt$median) || stt$valid_fraction<minvf)
      return(list(ok=FALSE,reason="CALIBRATION_INVALID_MIDPOINT",grid=diag,bisection_steps=step))
    if(abs(stt$median-target)<=tol)
      return(list(ok=TRUE,lambda=mid,pilot_median=stt$median,pilot_valid_fraction=stt$valid_fraction,grid=diag,bisection_steps=step))
    if((mlo-target)*(stt$median-target)<=0) hi<-mid else {lo<-mid;mlo<-stt$median}
  }
  list(ok=FALSE,reason="CALIBRATION_TOLERANCE_NOT_REACHED",grid=diag,bisection_steps=maxstep)
}

cal <- calibrate()
if(!isTRUE(cal$ok)){
  out <- list(version="v0.4.3",status="HOLD_BIEN_SPATIAL_INFORMATIVENESS_SYSTEM",
              system_id=system_id,family=family,trait_name=trait_name,semantic_class=semantic_class,
              outcome_blind=TRUE,real_trait_values_opened=FALSE,biological_turnover_outcomes_opened=FALSE,
              n_spatial_species=length(geoms),min_unique_nodes=min(vapply(geoms,function(g)g$n_nodes,integer(1))),
              max_unique_nodes=max(vapply(geoms,function(g)g$n_nodes,integer(1))),
              calibration=cal,system_spatial_pass=FALSE)
  write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
  cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
  quit(status=0)
}

reps <- as.integer(design$continuous_scalar_generator$evaluation_replicates)
eff <- family_effects(cal$lambda,reps,"evaluation")
good <- is.finite(eff)
vf <- mean(good)
target <- as.numeric(design$canonical_effect$benchmark_delta_rho)
mae <- if(any(good)) median(abs(eff[good]-target)) else Inf
directional <- sum(good & eff>0)/length(eff)
th <- design$canonical_effect$admission_thresholds
pass <- vf>=as.numeric(th$valid_replicate_fraction_min) &&
        directional>=as.numeric(th$directional_recovery_min) &&
        mae<=as.numeric(th$median_absolute_recovery_error_max)

out <- list(
  version="v0.4.3.1",
  status=if(pass)"BIEN_SPATIAL_INFORMATIVENESS_SYSTEM_PASS" else "HOLD_BIEN_SPATIAL_INFORMATIVENESS_SYSTEM",
  system_id=system_id,family=family,trait_name=trait_name,semantic_class=semantic_class,
  outcome_blind=TRUE,real_trait_values_opened=FALSE,biological_turnover_outcomes_opened=FALSE,
  n_spatial_species=length(geoms),
  min_unique_nodes=min(vapply(geoms,function(g)g$n_nodes,integer(1))),
  max_unique_nodes=max(vapply(geoms,function(g)g$n_nodes,integer(1))),
  min_records=min(vapply(geoms,function(g)g$n_records,numeric(1))),
  max_records=max(vapply(geoms,function(g)g$n_records,numeric(1))),
  lambda=cal$lambda,pilot_median=cal$pilot_median,pilot_valid_fraction=cal$pilot_valid_fraction,
  bisection_steps=cal$bisection_steps,median_absolute_recovery_error=mae,
  directional_recovery=directional,valid_replicate_fraction=vf,
  system_spatial_pass=pass,hold_reason=if(pass)"" else "RECOVERY_THRESHOLD_FAIL"
)
write_json(out,out_path,pretty=TRUE,auto_unbox=TRUE,null="null")
cat(toJSON(out,pretty=TRUE,auto_unbox=TRUE,null="null"),"\n")
