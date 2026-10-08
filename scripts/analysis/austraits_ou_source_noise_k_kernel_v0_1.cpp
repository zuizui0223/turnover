// O(n_edges) Blomberg K evaluation and shared-stationary-OU simulation.
// This uses the same Brownian GLS K normalization as phytools::phylosig.
// Rcpp exports consume ape 1-based cladewise edge matrices and postorder
// parent nodes. Independent Brownian process parameters are not tuned here.
#include <Rcpp.h>
#include <vector>
#include <cmath>
#include <stdexcept>
#include <limits>
using namespace Rcpp;

struct TreeK {
  int ntip;
  int nnode;
  int root;
  double norm;
  std::vector<int> parent;
  std::vector<int> child;
  std::vector<int> post;
  std::vector<double> length;
  std::vector<double> precision;
  std::vector<double> weight_sum;
  std::vector<std::vector<int>> incident;

  TreeK(const IntegerMatrix& e, const NumericVector& len,
        int nTip, const IntegerVector& internalPost,
        int rootNode, double traceCovariance) {
    ntip=nTip;
    int ne=e.nrow();
    if (len.size()!=ne || ne==0 || nTip<3)
      stop("Invalid edge matrix or tip count");
    int mx=rootNode;
    for (int i=0;i<ne;i++)
      mx=std::max(mx,std::max(e(i,0),e(i,1)));
    nnode=mx;
    root=rootNode-1;
    if (root<ntip || root>=nnode)
      stop("Root must be an internal node");
    incident.resize(nnode);
    parent.resize(ne);
    child.resize(ne);
    length.resize(ne);
    for(int i=0;i<ne;i++) {
      int p=e(i,0)-1,c=e(i,1)-1;
      if(p<0||c<0||p>=nnode||c>=nnode||p==c)
        stop("Out of range edge");
      if(!R_finite(len[i])||len[i]<0)
        stop("Invalid edge length");
      parent[i]=p;child[i]=c;length[i]=len[i];
      incident[p].push_back(i);
    }
    std::vector<double> ancvar(nnode,0.0);
    weight_sum.resize(nnode,0.0);
    post.reserve(internalPost.size());
    precision.resize(ne,0.0);
    for (int i=0;i<internalPost.size();i++) {
      int p=internalPost[i]-1;
      if(p<ntip||p>=nnode||incident[p].empty())
        stop("Postorder does not cover valid internal node");
      post.push_back(p);
      double s=0.0;
      for(int eidx: incident[p]) {
        double v=ancvar[child[eidx]]+length[eidx];
        if(!std::isfinite(v)||v<=0) stop("Nonpositive BM conditional variance");
        precision[eidx]=1.0/v;
        s+=precision[eidx];
      }
      ancvar[p]=1.0/s;
      weight_sum[p]=s;
    }
    if((int)post.size()!=nnode-ntip || post.back()!=root)
      stop("Expected every internal node and root last in postorder");
    norm=(traceCovariance-ntip*ancvar[root])/(ntip-1);
    if(!std::isfinite(norm)||norm<=0)stop("Invalid Brownian K normalization");
  }

  double fastK(const NumericVector& tip) const {
    if(tip.size()!=ntip)stop("K tip vector size mismatch");
    std::vector<double> val(nnode,0.0);
    for(int i=0;i<ntip;i++){
      val[i]=tip[i];
      if(!std::isfinite(val[i]))stop("Nonfinite K tip state");
    }
    double q=0.0;
    for(int p : post){
      double m=0;
      for(int ei: incident[p])
        m+=precision[ei]*val[child[ei]];
      m/=weight_sum[p];
      for(int ei: incident[p]){
        double dx=val[child[ei]]-m;
        q+=precision[ei]*dx*dx;
      }
      val[p]=m;
    }
    if(q<=0||!std::isfinite(q))stop("Invalid K inverse covariance quadratic");
    double a=val[root], numerator=0;
    for(int i=0;i<ntip;i++){
      double dx=tip[i]-a;
      numerator+=dx*dx;
    }
    double result=numerator/q/norm;
    if(!std::isfinite(result)||result<=0)stop("Invalid fast K");
    return result;
  }
};

// [[Rcpp::export]]
double fast_k_real_tree_cpp(IntegerMatrix edge, NumericVector len,
                            int nTip, IntegerVector internalPost,
                            int root, double traceCovariance,
                            NumericVector observedTips) {
  TreeK model(edge,len,nTip,internalPost,root,traceCovariance);
  return model.fastK(observedTips);
}

// [[Rcpp::export]]
NumericVector simulate_shared_ou_logK_cpp(
    IntegerMatrix edge, NumericVector len,
    int nTip, IntegerVector internalPost,
    int root, double traceCovariance,
    double alpha, int replicates) {
  Rcpp::RNGScope scope;
  if (!std::isfinite(alpha)||alpha<=0||replicates<1||replicates>4096)
    stop("Invalid OU alpha or replicate count");
  TreeK model(edge,len,nTip,internalPost,root,traceCovariance);
  int nn=model.nnode;
  int ne=model.child.size();
  std::vector<double> phi(ne),noise_sd(ne);
  for(int i=0;i<ne;i++){
    double h=alpha*model.length[i];
    phi[i]=std::exp(-h);
    noise_sd[i]=std::sqrt(-std::expm1(-2.0*h)/(2.0*alpha));
    if (!std::isfinite(noise_sd[i]))stop("Nonfinite OU noise variance");
  }
  double root_sd=std::sqrt(1.0/(2.0*alpha));
  NumericVector output(replicates), tips(nTip);
  std::vector<double> nodeState(nn,0.0);
  for(int b=0;b<replicates;b++){
    std::fill(nodeState.begin(),nodeState.end(),0.0);
    nodeState[model.root]=R::rnorm(0,root_sd);
    // Cladewise ape order is preorder: each edge's parent already exists.
    for(int i=0;i<ne;i++){
      int p=model.parent[i],c=model.child[i];
      nodeState[c]=phi[i]*nodeState[p]+noise_sd[i]*R::rnorm(0,1);
    }
    for(int j=0;j<nTip;j++)tips[j]=nodeState[j];
    output[b]=std::log(model.fastK(tips));
  }
  return output;
}


// [[Rcpp::export]]
Rcpp::List simulate_shared_ou_source_noise_logK_cpp(
    IntegerMatrix edge, NumericVector len, int nTip,
    IntegerVector internalPost, int root, double traceCovariance,
    double alpha, double etaGlobal, double etaLocal, int replicates) {
  Rcpp::RNGScope scope;
  if (!std::isfinite(alpha)||alpha<=0||
      !std::isfinite(etaGlobal)||etaGlobal<0||
      !std::isfinite(etaLocal)||etaLocal<0||
      replicates<1||replicates>4096)
    stop("Invalid fixed alpha/source noise ratio or count");
  TreeK model(edge,len,nTip,internalPost,root,traceCovariance);
  const int nn=model.nnode,ne=(int)model.child.size();
  std::vector<double> phi(ne),sd(ne),state(nn,0.0);
  for(int i=0;i<ne;i++){
    const double h=alpha*model.length[i];
    phi[i]=std::exp(-h);
    sd[i]=std::sqrt(-std::expm1(-2.0*h)/(2.0*alpha));
    if(!std::isfinite(sd[i]))stop("Nonfinite source-noise OU branch");
  }
  const double rootSD=std::sqrt(1/(2*alpha));
  NumericVector globalK(replicates),localK(replicates);
  NumericVector tipsG(nTip),tipsL(nTip);
  for(int b=0;b<replicates;b++){
    std::fill(state.begin(),state.end(),0.0);
    state[model.root]=R::rnorm(0,rootSD);
    for(int i=0;i<ne;i++){
      const int p=model.parent[i],c=model.child[i];
      state[c]=phi[i]*state[p]+sd[i]*R::rnorm(0,1);
    }
    double mean=0.0;
    for(int j=0;j<nTip;j++)mean+=state[j];
    mean/=nTip;
    double vv=0.0;
    for(int j=0;j<nTip;j++){
      double dif=state[j]-mean;
      vv+=dif*dif;
    }
    vv/=(nTip-1);
    if(!(vv>0)||!std::isfinite(vv))stop("Invalid latent tip spread");
    const double noiseG=std::sqrt(vv*etaGlobal),
                 noiseL=std::sqrt(vv*etaLocal);
    if(!std::isfinite(noiseG)||!std::isfinite(noiseL))
      stop("Invalid source noise scaling");
    for(int j=0;j<nTip;j++){
      const double z=R::rnorm(0,1);
      tipsG[j]=state[j]+noiseG*z;
      tipsL[j]=state[j]+noiseL*z;
    }
    globalK[b]=std::log(model.fastK(tipsG));
    localK[b]=std::log(model.fastK(tipsL));
  }
  return Rcpp::List::create(
    Rcpp::Named("trait_global")=globalK,
    Rcpp::Named("system_local")=localK);
}
