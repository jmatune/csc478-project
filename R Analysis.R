install.packages('devtools')
devtools::install_github('IRkernel/IRkernel')
# or devtools::install_local('IRkernel-master.tar.gz')
IRkernel::installspec()  # to register the kernel in the current R installation

library(corrplot)

data<-read.csv('processed_nodummies.csv')
data_cont<-data[c(3,9,10,11,26,27,28,29,31,34:53)]
corrplot(cor(data_cont), method="ellipse",order='AOE')

library(psych)
pca = psych::principal(data_cont, nfactors=10, scores=TRUE)
print(pca$loadings, cutoff=.4)
