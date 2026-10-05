#!/usr/bin/env Rscript
# AI-assisted development disclosure: ChatGPT (OpenAI; GPT-5.6 Sol) assisted with drafting/debugging this script. Author verification is required before submission.

weighted_midranks <- function(group_id,weights,n_groups){
  rs <- rowsum(matrix(weights,ncol=1),group=group_id,reorder=TRUE)
  gw <- numeric(n_groups)
  gw[as.integer(rownames(rs))] <- as.numeric(rs[,1])
  before <- c(0,head(cumsum(gw),-1))
  mid <- before + (gw+1)/2
  mid[group_id]
}

weighted_spearman_counts <- function(counts,pair_i,pair_j,gx,gy,nx,ny){
  w_self <- counts*(counts-1)/2
  w_pair <- counts[pair_i]*counts[pair_j]
  w <- c(w_self,w_pair)
  N <- sum(w)
  if(!is.finite(N) || N<=1) return(NA_real_)
  rx <- weighted_midranks(gx,w,nx)
  ry <- weighted_midranks(gy,w,ny)
  mu <- (N+1)/2
  dx <- rx-mu; dy <- ry-mu
  vx <- sum(w*dx*dx)
  vy <- sum(w*dy*dy)
  if(vx<=0 || vy<=0) return(NA_real_)
  z <- sum(w*dx*dy)/sqrt(vx*vy)
  if(!is.finite(z)) return(NA_real_)
  as.numeric(z)
}

one_case <- function(n,seed,reps=100L){
  set.seed(seed)
  # Symmetric positive distance matrix with realistic ties introduced by rounding.
  xy <- matrix(rnorm(n*3),ncol=3)
  D <- as.matrix(dist(xy))
  D <- round(D,3)
  diag(D) <- 0
  state <- round(rnorm(n),2)

  ij <- which(lower.tri(D),arr.ind=TRUE)
  pair_i <- ij[,1]; pair_j <- ij[,2]
  sep_cat <- c(rep(0,n),D[ij])
  diss_cat <- c(rep(0,n),abs(state[pair_i]-state[pair_j]))
  gx <- match(sep_cat,sort(unique(sep_cat)))
  gy <- match(diss_cat,sort(unique(diss_cat)))
  nx <- max(gx); ny <- max(gy)

  err <- numeric(reps)
  valid <- logical(reps)
  for(b in seq_len(reps)){
    idx <- sample.int(n,n,replace=TRUE)
    counts <- tabulate(idx,nbins=n)

    direct <- suppressWarnings(cor(
      as.numeric(as.dist(D[idx,idx,drop=FALSE])),
      as.numeric(dist(state[idx])),
      method="spearman",
      use="complete.obs"
    ))
    weighted <- weighted_spearman_counts(counts,pair_i,pair_j,gx,gy,nx,ny)

    if(is.finite(direct) && is.finite(weighted)){
      valid[[b]] <- TRUE
      err[[b]] <- abs(direct-weighted)
    } else if(is.na(direct) && is.na(weighted)){
      valid[[b]] <- TRUE
      err[[b]] <- 0
    } else {
      stop(sprintf("finite-status mismatch n=%d replicate=%d direct=%s weighted=%s",
                   n,b,as.character(direct),as.character(weighted)))
    }
  }
  if(!all(valid)) stop("invalid synthetic comparison")
  max(err)
}

e8 <- one_case(8,2026100508L,100L)
e12 <- one_case(12,2026100512L,100L)
mx <- max(e8,e12)
cat(sprintf("n=8 max_abs_error=%.17g\n",e8))
cat(sprintf("n=12 max_abs_error=%.17g\n",e12))
cat(sprintf("overall max_abs_error=%.17g\n",mx))
if(!is.finite(mx) || mx>1e-12)
  stop(sprintf("weighted Spearman equivalence failed: %.17g",mx))
