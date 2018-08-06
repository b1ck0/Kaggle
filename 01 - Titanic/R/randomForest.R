train = read.csv("train.csv", stringsAsFactors = F)
test = read.csv("test.csv", stringsAsFactors = F)

library(randomForest)
library(ROCR)
library(mice)
library(caret)
library(e1071)

imputed = complete(mice(train,m=5,maxit=50,meth='pmm',seed=500))
imputed.test = complete(mice(test,m=5,maxit=50,meth='pmm',seed=500))

imputed$Survived = as.factor(imputed$Survived)
imputed$Sex = as.factor(imputed$Sex)

imputed.test$Sex = as.factor(imputed.test$Sex)

Forest1 = randomForest(Survived ~ Age + Sex + SibSp + Parch + Fare, data = imputed)
Forest1.pred = predict(Forest1)

a = table(imputed$Survived, Forest1.pred)
(a[1,1]+a[2,2])/sum(a) #accuracy
varImpPlot(Forest1)
vu = varUsed(Forest1, count=TRUE)
vusorted = sort(vu, decreasing = FALSE, index.return = TRUE)
dotchart(vusorted$x, names(Forest1$forest$xlevels[vusorted$ix]))

prediction3 <- predict(Forest1, newdata=imputed.test, type = "class")
solution3 <- data.frame(PassengerID = test$PassengerId, Survived = as.numeric(prediction3)-1)
write.csv(solution3, file = 'model4_Solution.csv', row.names = F)

#####################################################################
