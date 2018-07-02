import os, sys
import pandas as pd
import numpy as np
from sklearn import tree, ensemble, neighbors, linear_model, neural_network, svm, naive_bayes
from sklearn import model_selection, metrics
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QFileDialog
from PyQt5.QtWidgets import QPushButton, QRadioButton
from PyQt5.QtWidgets import QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit, QTextEdit, QLabel
from PyQt5.QtWidgets import QStackedWidget, QGroupBox, QFrame, QTableWidget, QTreeWidget, QTreeWidgetItem, QListView
from PyQt5.QtWidgets import QFormLayout, QGridLayout, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QIcon, QPixmap

from data import Data
from model import Model

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.leftPanel = QStackedWidget(self)
        self.rightPanel = QGroupBox(self)
        self.initUI()

    def __setLabel(self, str, parent, font=QFont()):
        label = QLabel(str, parent)
        label.setFont(font)
        return label

    def __setSpinBox(self, val, min, max, stepsize, parent):
        box = QSpinBox(parent)
        box.setMinimum(min)
        box.setMaximum(max)
        box.setSingleStep(stepsize)
        box.setValue(val)
        return box

    def __setDoubleSpinBox(self, val, min, max, stepsize, prec, parent):
        box = QDoubleSpinBox(parent)
        box.setMinimum(min)
        box.setMaximum(max)
        box.setSingleStep(stepsize)
        box.setValue(val)
        box.setDecimals(prec)
        return box

    def __openLabeledFile(self):
        path = QFileDialog.getOpenFileName(self.dataPage, 'Select File...')
        path = path[0]

        if path is not '':
        	name = os.path.basename(path)
        	self.labeledFileDisplay.setText(name)
        	data = pd.read_csv(path, delimiter=',')
        	self.labeled_data = Data(data, name, True)
        	self.dataSummaryTree.takeTopLevelItem(0)
        	self.__getDataSummary(self.labeled_data)
        	self.splitFrame.setEnabled(True)
        	self.validationFrame.setEnabled(True)
        	self.dataNextPushButton.setEnabled(True)

    def __openUnlabeledFile(self):
        path = QFileDialog.getOpenFileName(self.dataPage, 'Select File...')
        path = path[0]

        if path is not '':
        	name = os.path.basename(path)
        	self.unlabeledFileDisplay.setText(name)
        	data = pd.read_csv(path, delimiter=',')
        	self.unlabeled_data = Data(data, name, False)
        	self.dataSummaryTree.takeTopLevelItem(1)
        	self.__getDataSummary(self.unlabeled_data)
        	self.predictionPushButton.setEnabled(True)

    def __getDataSummary(self, data):
        fileName = QTreeWidgetItem(self.dataSummaryTree)
        fileName.setText(0, data.getName())
        sampleSubTree = QTreeWidgetItem(fileName)
        sampleSubTree.setText(0, 'Samples')
        sampleSubTree.setText(1, str(data.getNumOfSamples()))
        classCountsDict = data.getClassCounts()

        for className in classCountsDict:
        	cls = QTreeWidgetItem(sampleSubTree)
        	cls.setText(0, className)
        	cls.setText(1, str(classCountsDict[className]))
        	cls.setToolTip(0, className)

        featureSubTree = QTreeWidgetItem(fileName)
        featureSubTree.setText(0, 'Features')
        featureSubTree.setText(1, str(data.getNumOfFeatures()))
        featureTypeDict = data.getFeatureTypes()

        for featureName in featureTypeDict:
        	feature = QTreeWidgetItem(featureSubTree)
        	feature.setText(0, featureName)
        	feature.setText(1, featureTypeDict[featureName])
        	feature.setToolTip(0, featureName)

        # if data has been transformed, show statistics of transformed data
        if data.isTransformed():
            transformedFeatureSubTree = QTreeWidgetItem(fileName)
            transformedFeatureSubTree.setText(0, 'Transformed Features')
            transformedFeatureSubTree.setText(1, str(data.getNumOfTransformedFeatures()))
            transformedFeatureTypeDict = data.getTransformedFeatureTypes()

            for transformedFeatureName in transformedFeatureTypeDict:
                transformedFeature = QTreeWidgetItem(transformedFeatureSubTree)
                transformedFeature.setText(0, transformedFeatureName)
                transformedFeature.setText(1, transformedFeatureTypeDict[transformedFeatureName])
                transformedFeature.setToolTip(0, transformedFeatureName)

    def __trainTestSplit(self):
        test_size = self.splitSpinBox.value() / 100
        stratify = self.splitCheckBox.isChecked()
        self.labeled_data.trainTestSplit(test_size, stratify)

    def __holdOutTest(self, X, y, classifier, classifier_type, val_size, stratify):
        if stratify:
            s = y
        else:
            s = None

        X_train, X_val, y_train, y_val = model_selection.train_test_split(\
            X, y, test_size=val_size, stratify=s, random_state=0)

        classifier = classifier.fit(X_train, y_train)
        y_pred = classifier.predict(X_val)
        accuracy = metrics.accuracy_score(y_val, y_pred)
        class_precision = metrics.precision_score(y_val, y_pred, average=None)
        class_recall = metrics.recall_score(y_val, y_pred, average=None)
        class_f1 = metrics.f1_score(y_val, y_pred, average=None)
        confusion_matrix = metrics.confusion_matrix(y_val, y_pred)
        confusion_matrix = confusion_matrix / np.sum(confusion_matrix, axis=1)
        
        return Model(classifier_type, accuracy, class_precision, class_recall, \
            class_f1, confusion_matrix)

    def __kFoldCrossValidation(self, X, y, classifier, classifier_type, k, stratify):
        num_classes = self.labeled_data.getNumOfClasses()
        accuracy = 0
        class_precision = np.zeros(num_classes)
        class_recall = np.zeros(num_classes)
        class_f1 = np.zeros(num_classes)
        confusion_matrix = np.zeros([num_classes, num_classes])

        if stratify:
            kf = model_selection.StratifiedKFold(n_splits=k, shuffle=True, random_state=0)
        else:
            kf = model_selection.KFold(n_splits=k, shuffle=True, random_state=0)
            
        for train_idx, val_idx in kf.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            classifier = classifier.fit(X_train, y_train)
            y_pred = classifier.predict(X_val)
            accuracy += metrics.accuracy_score(y_val, y_pred)
            class_precision += metrics.precision_score(y_val, y_pred, average=None)
            class_recall += metrics.recall_score(y_val, y_pred, average=None)
            class_f1 += metrics.f1_score(y_val, y_pred, average=None)
            confusion_matrix += metrics.confusion_matrix(y_val, y_pred)

        # average over all folds
        accuracy /= k
        class_precision /= k
        class_recall /= k
        class_f1 /= k
        confusion_matrix = confusion_matrix / np.sum(confusion_matrix, axis=1)

        return Model(classifier_type, accuracy, class_precision, class_recall, \
            class_f1, confusion_matrix)

    def __leaveOneOutTest(self, X, y, classifier, classifier_type):
        kf = model_selection.KFold(n_splits=X.shape[0])
        y_pred = model_selection.cross_val_predict(classifier, X, y, cv=kf.split(X, y))

        accuracy = metrics.accuracy_score(y, y_pred)
        class_precision = metrics.precision_score(y, y_pred, average=None)
        class_recall = metrics.recall_score(y, y_pred, average=None)
        class_f1 = metrics.f1_score(y, y_pred, average=None)
        confusion_matrix = metrics.confusion_matrix(y, y_pred)
        confusion_matrix = confusion_matrix / np.sum(confusion_matrix, axis=1)
        
        return Model(classifier_type, accuracy, class_precision, class_recall, \
            class_f1, confusion_matrix)

    def __trainAndValidate(self, X, y, classifier, classifier_type):
        stratify = self.validationCheckBox.isChecked()

        if self.holdoutRadioButton.isChecked():
            val_size = self.holdoutSpinBox.value() / 100
            return self.__holdOutTest(X, y, classifier, classifier_type, val_size, stratify)

        if self.cvRadioButton.isChecked():
            k = self.cvSpinBox.value()
            return self.__kFoldCrossValidation(X, y, classifier, classifier_type, k, stratify)

        if self.looRadioButton.isChecked():
            return self.__leaveOneOutTest(X, y, classifier, classifier_type)

    def __trainDecisionTree(self):
        data = self.labeled_data.getTrain()
        num_features = self.labeled_data.getNumOfFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        max_depth = self.dtMaxDepthLineEdit.text()
        if max_depth == 'None':
            max_depth = None

        class_weight = self.dtClassWeightComboBox.currentText()
        if class_weight == 'uniform':
            class_weight = None

        dt = tree.DecisionTreeClassifier(\
            criterion = self.dtCriterionComboBox.currentText(), \
            max_depth = max_depth, \
            min_samples_split = self.dtMinSamplesSplitSpinBox.value(), \
            min_samples_leaf = self.dtMinSamplesLeafSpinBox.value(), \
            class_weight = class_weight)
        return self.__trainAndValidate(X, y, dt, 'decision tree')

    def __trainRandomForest(self):
        data = self.labeled_data.getTrain()
        num_features = self.labeled_data.getNumOfFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        max_features = self.rfMaxFeaturesComboBox.currentText()
        if max_depth == 'all':
            max_depth = None

        class_weight = self.rfClassWeightComboBox.currentText()
        if class_weight == 'uniform':
            class_weight = None

        rf = ensemble.RandomForestClassifier(\
            n_estimators = self.rfNumEstimatorsSpinBox.value(), \
            criterion = self.rfCriterionComboBox.currentText(), \
            max_depth = self.rfMaxDepthLineEdit.text(), \
            min_samples_split = self.rfMinSamplesSplitSpinBox.value(), \
            min_samples_leaf = self.rfMinSamplesLeafSpinBox.value(), \
            max_features = max_features, \
            bootstrap = self.rfBootstrapCheckBox.isChecked(), \
            class_weight = class_weight)
        return self.__trainAndValidate(X, y, rf, 'random forest')

    def __trainKNearestNeighbors(self):
        data = self.labeled_data.getTransformedTrain()
        num_features = self.labeled_data.getNumOfTransformedFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        knn = neighbors.KNeighborsClassifier(\
            n_neighbors = self.knnNumNeighborsSpinBox.value(), \
            weights = self.knnWeightsComboBox.currentText(), \
            metric = self.knnMetricComboBox.currentText())
        return self.__trainAndValidate(X, y, knn, 'k-nearset neighbors')

    def __trainLogisticRegression(self):
        data = self.labeled_data.getTransformedTrain()
        num_features = self.labeled_data.getNumOfTransformedFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        class_weight = self.lrClassWeightComboBox.currentText()
        if class_weight == 'uniform':
            class_weight = None

        lr = linear_model.LogisticRegression(\
            penalty = self.lrRegularizationComboBox.currentText(), \
            tol = self.lrTolLineEdit.text(), \
            C = self.lrRglrStrengthDoubleSpinBox.value(), \
            fit_intercept = self.lrFitInterceptCheckBox.isChecked(), \
            class_weight = class_weight, \
            solver = 'saga', \
            max_iter = self.lrMaxIterLineEdit.text(), \
            multi_class = self.lrMultiClassComboBox.currentText())
        return self.__trainAndValidate(X, y, lr, 'logistic regression')
        
    def __trainNeuralNetwork(self):
        data = self.labeled_data.getTransformedTrain()
        num_features = self.labeled_data.getNumOfTransformedFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        nn = neural_network.MLPClassifier(\
            hidden_layer_sizes = self.nnNumHiddenUnitsSpinBox.value(), \
            activation = self.nnActivationComboBox.currentText(), \
            solver = 'sgd', \
            batch_size = self.nnBatchSizeLineEdit.text(), \
            learning_rate = self.nnLearningRateComboBox.currentText(), \
            learning_rate_init = self.nnLearningRateInitLineEdit(), \
            max_iter = self.nnMaxIterLineEdit.text(), \
            tol = self.nnTolLineEdit.text(), \
            early_stopping = self.nnEarlyStoppingCheckBox.isChecked())
        return self.__trainAndValidate(X, y, nn, 'neural network')

    def __trainSVM(self):
        data = self.labeled_data.getTransformedTrain()
        num_features = self.labeled_data.getNumOfTransformedFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        class_weight = self.svmClassWeightComboBox.currentText()
        if class_weight == 'uniform':
            class_weight = None

        svm = svm.SVC(\
            C = self.svmPenaltyDoubleSpinBox.value(), \
            kernel = self.svmKernelComboBox.currentText(), \
            degree = self.svmDegreeSpinBox.value(), \
            gamma = self.svmGammaLineEdit.text(), \
            coef0 = self.svmCoefDoubleSpinBox.value(), \
            probability = True, \
            tol = self.svmTolLineEdit.text(), \
            class_weight = class_weight, \
            max_iter = self.svmMaxIterLineEdit.text())
        return self.__trainAndValidate(X, y, svm, 'svm')

    def __trainNaiveBayes(self):
        data = self.labeled_data.getTrain()
        num_features = self.labeled_data.getNumOfTransformedFeatures()
        X = data.iloc[:, 0: num_features]
        y = data.iloc[:, num_features]

        # string-valued features: use multinomial NB
        if self.labeled_data.getFeatureSummary() == 'string':
            nb = naive_bayes.MultinomialNB(\
                alpha = self.nbAddSmoothDoubleSpinBox.value(), \
                fit_prior = self.nbFitPriorCheckBox.isChecked(), \
                class_prior = self.nbClassPriorLineEdit.text())

        # numeric features: use gaussian NB
        elif self.labeled_data.getFeatureSummary() == 'numeric':
            nb = naive_bayes.GaussianNB(\
                priors = self.nbClassPriorLineEdit.text())
        
        return self.__trainAndValidate(X, y, nb, 'naive bayes')

    def __trainClassifier(self):
        index = self.paramStack.currentIndex()

        if index == 1:
            model = self.__trainDecisionTree()
        elif index == 2:
            model = self.__trainRandomForest()
        elif index == 3:
            model = self.__trainKNearestNeighbors()
        elif index == 4:
            model = self.__trainLogisticRegression()
        elif index == 5:
            model = self.__trainNeuralNetwork()
        elif index == 6:
            model = self.__trainSVM()
        elif index == 7:
            model = self.__trainNaiveBayes()

        name = self.classNameLineEdit.text()
        if name is not '':
            model.setName(name)
        model.setComment(self.classCommentTextEdit.toPlainText())

        self.models.append(model)

        # TODO: add model to the ListView

    def knnPreSet(self):
        # string-valued features: use hamming distance
        if self.labeled_data.getFeatureSummary() == 'string':
            self.knnMetricListView.setRowHidden(0, True)
            self.knnMetricListView.setRowHidden(1, True)
        # numeric features: use euclidean or manhatten distance
        elif self.labeled_data.getFeatureSummary() == 'numeric':
            self.knnMetricListView.setRowHidden(2, True)
        # mixed features: DO NOT use KNN
        else:
            self.classTypeListView.setRowHidden(3, True)

    def nbPreSet(self):
        # string-valued features: use multinomial NB
        if self.labeled_data.getFeatureSummary() == 'string':
            self.nbDistributionLabel.setText('multinomial')
        # numeric features: use gaussian NB
        elif self.labeled_data.getFeatureSummary() == 'numeric':
            self.nbDistributionLabel.setText('gaussian')
            self.nbAddSmoothDoubleSpinBox.setDisabled(True)
            self.nbFitPriorCheckBox.setDisabled(True)
        # mixed features: DO NOT use NB
        else:
            self.classTypeListView.setRowHidden(7, True)
    
    def initUI(self):
        self.models = []                # a collection of all trained models

        titleFont = QFont()
        titleFont.setBold(True)

        ########## 1st page: data loading and splitting ##########
        self.dataPage = QWidget()
        openIcon = QIcon('icons/open.png')
        dataPageLayout = QVBoxLayout(self.dataPage)

        ### load labeled data
        labeledDataLabel = self.__setLabel('Labeled Data:', self.dataPage, titleFont)
        labeledFilePushButton = QPushButton('Select File...', self.dataPage)
        labeledFilePushButton.setIcon(openIcon)
        labeledFilePushButton.setMaximumWidth(140)
        labeledFileSpacer = QSpacerItem(40, 20)
        self.labeledFileDisplay = QLabel('<filename>', self.dataPage)

        dataPageLayout.addWidget(labeledDataLabel)
        labeledFileLayout = QHBoxLayout()
        labeledFileLayout.addWidget(labeledFilePushButton)
        labeledFileLayout.addItem(labeledFileSpacer)
        labeledFileLayout.addWidget(self.labeledFileDisplay)
        dataPageLayout.addLayout(labeledFileLayout)

        labeledFilePushButton.clicked.connect(self.__openLabeledFile)

        ### load unlabeled data
        unlabeledDataLabel = self.__setLabel('Unlabeled Data:', self.dataPage, titleFont)
        unlabeledFilePushButton = QPushButton('Select File...', self.dataPage)
        unlabeledFilePushButton.setIcon(openIcon)
        unlabeledFilePushButton.setMaximumWidth(140)
        unlabeledFileSpacer = QSpacerItem(40, 20)
        self.unlabeledFileDisplay = QLabel('<filename>', self.dataPage)

        dataPageLayout.addWidget(unlabeledDataLabel)
        unlabeledFileLayout = QHBoxLayout()
        unlabeledFileLayout.addWidget(unlabeledFilePushButton)
        unlabeledFileLayout.addItem(unlabeledFileSpacer)
        unlabeledFileLayout.addWidget(self.unlabeledFileDisplay)
        dataPageLayout.addLayout(unlabeledFileLayout)

        unlabeledFilePushButton.clicked.connect(self.__openUnlabeledFile)

        ### data summary
        dataSummaryLabel = self.__setLabel('Data Summary:', self.dataPage, titleFont)
        self.dataSummaryTree = QTreeWidget(self.dataPage)
        self.dataSummaryTree.setColumnCount(2)
        self.dataSummaryTree.setHeaderHidden(True)
        self.dataSummaryTree.setColumnWidth(0, 200)
        dataPageLayout.addWidget(dataSummaryLabel)
        dataPageLayout.addWidget(self.dataSummaryTree)

        ### train/test split
        trainTestLabel = self.__setLabel('Train/Test Split:', self.dataPage, titleFont)
        self.splitFrame = QFrame(self.dataPage)
        self.splitFrame.setAutoFillBackground(True)
        self.splitFrame.setDisabled(True)
        self.splitSpinBox = self.__setSpinBox(20, 10, 50, 10, self.splitFrame)
        self.splitSpinBox.setMaximumWidth(60)
        splitLabel = self.__setLabel('% for test', self.splitFrame)
        self.splitCheckBox = QCheckBox('Stratified Sampling', self.splitFrame)
        self.splitCheckBox.setChecked(True)

        dataPageLayout.addWidget(trainTestLabel)
        trainTestLayout = QHBoxLayout()
        trainTestLayout.addWidget(self.splitSpinBox)
        trainTestLayout.addWidget(splitLabel)
        trainTestLayout.addWidget(self.splitCheckBox)
        splitLayout = QVBoxLayout(self.splitFrame)
        splitLayout.addLayout(trainTestLayout)
        dataPageLayout.addWidget(self.splitFrame)

        ### validation methodology
        validationLabel = self.__setLabel('Validation Methodology:', self.dataPage, titleFont)
        self.validationFrame = QFrame(self.dataPage)
        self.validationFrame.setAutoFillBackground(True)
        self.validationFrame.setDisabled(True)
        self.holdoutRadioButton = QRadioButton('Holdout Validation', self.validationFrame)
        self.cvRadioButton = QRadioButton('K-Fold Cross-Validation', self.validationFrame)
        self.cvRadioButton.setChecked(True)
        self.looRadioButton = QRadioButton('Leave-One-Out Validation', self.validationFrame)
        holdoutSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        cvSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        looSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        validationSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.holdoutSpinBox = self.__setSpinBox(20, 10, 50, 10, self.validationFrame)
        self.holdoutSpinBox.setMaximumWidth(50)
        self.holdoutSpinBox.setDisabled(True)
        self.cvSpinBox = self.__setSpinBox(10, 5, 20, 5, self.validationFrame)
        self.validationCheckBox = QCheckBox('Stratified Sampling', self.validationFrame)
        self.validationCheckBox.setChecked(True)
        holdoutLabel = self.__setLabel('% for validation', self.validationFrame)
        cvLabel = self.__setLabel('folds', self.validationFrame)

        self.holdoutRadioButton.toggled.connect(self.holdoutSpinBox.setEnabled)
        self.holdoutRadioButton.toggled.connect(self.cvSpinBox.setDisabled)
        self.holdoutRadioButton.toggled.connect(self.validationCheckBox.setEnabled)
        self.cvRadioButton.toggled.connect(self.holdoutSpinBox.setDisabled)
        self.cvRadioButton.toggled.connect(self.cvSpinBox.setEnabled)
        self.cvRadioButton.toggled.connect(self.validationCheckBox.setEnabled)
        self.looRadioButton.toggled.connect(self.holdoutSpinBox.setDisabled)
        self.looRadioButton.toggled.connect(self.cvSpinBox.setDisabled)
        self.looRadioButton.toggled.connect(self.validationCheckBox.setDisabled)

        dataPageLayout.addWidget(validationLabel)
        holdoutLayout = QHBoxLayout()
        holdoutLayout.addWidget(self.holdoutRadioButton)
        holdoutLayout.addItem(holdoutSpacer)
        holdoutLayout.addWidget(self.holdoutSpinBox)
        holdoutLayout.addWidget(holdoutLabel)
        cvLayout = QHBoxLayout()
        cvLayout.addWidget(self.cvRadioButton)
        cvLayout.addItem(cvSpacer)
        cvLayout.addWidget(self.cvSpinBox)
        cvLayout.addWidget(cvLabel)
        looLayout = QHBoxLayout()
        looLayout.addWidget(self.looRadioButton)
        looLayout.addItem(looSpacer)
        samplingLayout = QHBoxLayout()
        samplingLayout.addItem(validationSpacer)
        samplingLayout.addWidget(self.validationCheckBox)
        validationLayout = QVBoxLayout(self.validationFrame)
        validationLayout.addLayout(holdoutLayout)
        validationLayout.addLayout(cvLayout)
        validationLayout.addLayout(looLayout)
        validationLayout.addLayout(samplingLayout)
        dataPageLayout.addWidget(self.validationFrame)

        ### data spacer and line
        dataSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        dataPageLayout.addItem(dataSpacer)
        dataLine = QFrame(self.dataPage)
        dataLine.setFrameShape(QFrame.HLine)
        dataLine.setFrameShadow(QFrame.Sunken)
        dataPageLayout.addWidget(dataLine)

        ### next button
        dataNextSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.dataNextPushButton = QPushButton('Next', self.dataPage)
        self.dataNextPushButton.setDefault(True)
        self.dataNextPushButton.setMinimumWidth(90)
        self.dataNextPushButton.setDisabled(True)
        self.dataNextPushButton.clicked.connect(lambda: self.leftPanel.setCurrentIndex(1))
        self.dataNextPushButton.clicked.connect(self.__trainTestSplit)
        self.dataNextPushButton.clicked.connect(self.knnPreSet)
        self.dataNextPushButton.clicked.connect(self.nbPreSet)
        self.dataNextPushButton.clicked.connect(\
            lambda: self.svmGammaLineEdit.setText(str(round(1/self.labeled_data.getNumOfFeatures(), 2))))
        dataNextLayout = QHBoxLayout()
        dataNextLayout.addItem(dataNextSpacer)
        dataNextLayout.addWidget(self.dataNextPushButton)
        dataPageLayout.addLayout(dataNextLayout)

        self.leftPanel.addWidget(self.dataPage)


        ########## 2nd page: training ##########

        modelPage = QWidget()
        modelPageLayout = QVBoxLayout(modelPage)

        ### classifier type
        classTypeLabel = self.__setLabel('Classifier Type:', modelPage, titleFont)
        self.classTypeComboBox = QComboBox(modelPage)
        self.classTypeListView = self.classTypeComboBox.view()
        classTypeLayout = QHBoxLayout()
        classTypeLayout.addWidget(classTypeLabel)
        classTypeLayout.addWidget(self.classTypeComboBox)

        ### classifier parameter stack
        self.paramStack = QStackedWidget(modelPage)
        self.paramStack.setMinimumHeight(320)
        self.classTypeComboBox.currentIndexChanged.connect(self.paramStack.setCurrentIndex)

        modelPageLayout.addLayout(classTypeLayout)
        modelPageLayout.addWidget(self.paramStack)

        ## initial empty page
        noneIcon = QIcon('icons/none.png')
        self.classTypeComboBox.addItem(noneIcon, '-- Select Classifier --')
        initPage = QWidget()
        self.paramStack.addWidget(initPage)

        ## decision tree
        dtIcon = QIcon('icons/dt.png')
        self.classTypeComboBox.addItem(dtIcon, 'Decision Tree')
        dtPage = QWidget()
        self.paramStack.addWidget(dtPage)

        # fields
        self.dtCriterionComboBox = QComboBox(dtPage)
        self.dtCriterionComboBox.addItem('gini')
        self.dtCriterionComboBox.addItem('entropy')
        self.dtMaxDepthLineEdit = QLineEdit('None', dtPage)
        self.dtMinSamplesSplitSpinBox = self.__setSpinBox(2, 2, 20, 1, dtPage)
        self.dtMinSamplesLeafSpinBox = self.__setSpinBox(1, 1, 20, 1, dtPage)
        self.dtClassWeightComboBox = QComboBox(dtPage)
        self.dtClassWeightComboBox.addItem('uniform')
        self.dtClassWeightComboBox.addItem('balanced')

        # layout
        dtLayout = QFormLayout()
        dtLayout.addRow('criterion:', self.dtCriterionComboBox)
        dtLayout.addRow('max_depth:', self.dtMaxDepthLineEdit)
        dtLayout.addRow('min_samples_split:', self.dtMinSamplesSplitSpinBox)
        dtLayout.addRow('min_samples_leaf:', self.dtMinSamplesLeafSpinBox)
        dtLayout.addRow('class_weight:', self.dtClassWeightComboBox)

        dtPageLayout = QVBoxLayout(dtPage)
        dtPageLayout.addLayout(dtLayout)

        ## Random forest
        rfIcon = QIcon('icons/rf.png')
        self.classTypeComboBox.addItem(rfIcon, 'Random Forest')
        rfPage = QWidget()
        self.paramStack.addWidget(rfPage)

        # fields
        self.rfCriterionComboBox = QComboBox(rfPage)
        self.rfCriterionComboBox.addItem('gini')
        self.rfCriterionComboBox.addItem('entropy')
        self.rfNumEstimatorsSpinBox = self.__setSpinBox(10, 1, 25, 1, rfPage)
        self.rfMaxFeaturesComboBox = QComboBox(rfPage)
        self.rfMaxFeaturesComboBox.addItem('sqrt')
        self.rfMaxFeaturesComboBox.addItem('log2')
        self.rfMaxFeaturesComboBox.addItem('all')
        self.rfMaxDepthLineEdit = QLineEdit('None', rfPage)
        self.rfMinSamplesSplitSpinBox = self.__setSpinBox(2, 2, 20, 1, rfPage)
        self.rfMinSamplesLeafSpinBox = self.__setSpinBox(1, 1, 20, 1, rfPage)
        self.rfBootstrapCheckBox = QCheckBox('', rfPage)
        self.rfBootstrapCheckBox.setChecked(True)
        self.rfClassWeightComboBox = QComboBox(rfPage)
        self.rfClassWeightComboBox.addItem('uniform')
        self.rfClassWeightComboBox.addItem('balanced')

        # layout
        rfLayout = QFormLayout()
        rfLayout.addRow('criterion:', self.rfCriterionComboBox)
        rfLayout.addRow('n_estimators:', self.rfNumEstimatorsSpinBox)
        rfLayout.addRow('max_features:', self.rfMaxFeaturesComboBox)
        rfLayout.addRow('max_depth:', self.rfMaxDepthLineEdit)
        rfLayout.addRow('min_samples_split:', self.rfMinSamplesSplitSpinBox)
        rfLayout.addRow('min_samples_leaf:', self.rfMinSamplesLeafSpinBox)
        rfLayout.addRow('bootstrap:', self.rfBootstrapCheckBox)
        rfLayout.addRow('class_weight:', self.rfClassWeightComboBox)

        rfPageLayout = QVBoxLayout(rfPage)
        rfPageLayout.addLayout(rfLayout)

        ## K-nearest neighbors
        knnIcon = QIcon('icons/knn.png')
        self.classTypeComboBox.addItem(knnIcon, 'K-Nearest Neighbors')
        knnPage = QWidget()
        self.paramStack.addWidget(knnPage)

        # fields
        self.knnNumNeighborsSpinBox = self.__setSpinBox(5, 1, 20, 1, knnPage)
        self.knnWeightsComboBox = QComboBox(knnPage)
        self.knnWeightsComboBox.addItem('uniform')
        self.knnWeightsComboBox.addItem('distance')
        self.knnMetricComboBox = QComboBox(knnPage)
        self.knnMetricListView =self.knnMetricComboBox.view() # see knnSetHidden()
        self.knnMetricComboBox.addItem('euclidean') #
        self.knnMetricComboBox.addItem('manhattan') # DO NOT change order
        self.knnMetricComboBox.addItem('hamming')   #

        # layout
        knnLayout = QFormLayout()
        knnLayout.addRow('n_neighbors:', self.knnNumNeighborsSpinBox)
        knnLayout.addRow('weights:', self.knnWeightsComboBox)
        knnLayout.addRow('metric:', self.knnMetricComboBox)

        knnPageLayout = QVBoxLayout(knnPage)
        knnPageLayout.addLayout(knnLayout)

        ## Logistic regression
        lrIcon = QIcon('icons/lr.png')
        self.classTypeComboBox.addItem(lrIcon, 'Logistic Regression')
        lrPage = QWidget()
        self.paramStack.addWidget(lrPage)

        # fields
        self.lrRegularizationComboBox = QComboBox(lrPage)
        self.lrRegularizationComboBox.addItem('l2')
        self.lrRegularizationComboBox.addItem('l1')
        self.lrRglrStrengthDoubleSpinBox = self.__setDoubleSpinBox(1, 0, 10, 0.1, 1, lrPage)
        self.lrFitInterceptCheckBox = QCheckBox('', lrPage)
        self.lrFitInterceptCheckBox.setChecked(True)
        self.lrMultiClassComboBox = QComboBox(lrPage)
        self.lrMultiClassComboBox.addItem('ovr')
        self.lrMultiClassComboBox.addItem('multinomial')
        self.lrClassWeightComboBox = QComboBox(lrPage)
        self.lrClassWeightComboBox.addItem('uniform')
        self.lrClassWeightComboBox.addItem('balanced')

        lrStopLabel = QLabel('Stopping Criteria:', lrPage)
        lrTolLabel = QLabel('tol:', lrPage)
        lrTolLabel.setMinimumWidth(60)
        self.lrTolLineEdit = QLineEdit('1e-3', lrPage)
        lrMaxIterLabel = QLabel('max_iter:', lrPage)
        lrMaxIterLabel.setMinimumWidth(60)
        self.lrMaxIterLineEdit = QLineEdit('100', lrPage)

        # layout
        lrLayout = QFormLayout()
        lrLayout.addRow('regularization:', self.lrRegularizationComboBox)
        lrLayout.addRow('rglr_strength:', self.lrRglrStrengthDoubleSpinBox)
        lrLayout.addRow('fit_intercept:', self.lrFitInterceptCheckBox)
        lrLayout.addRow('multi_class:', self.lrMultiClassComboBox)
        lrLayout.addRow('class_weight:', self.lrClassWeightComboBox)

        lrSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        lrStopLayout = QHBoxLayout()
        lrStopLayout.addWidget(lrTolLabel)
        lrStopLayout.addWidget(self.lrTolLineEdit)
        lrStopLayout.addWidget(lrMaxIterLabel)
        lrStopLayout.addWidget(self.lrMaxIterLineEdit)

        lrPageLayout = QVBoxLayout(lrPage)
        lrPageLayout.addLayout(lrLayout)
        lrPageLayout.addItem(lrSpacer)
        lrPageLayout.addWidget(lrStopLabel)
        lrPageLayout.addLayout(lrStopLayout)

        ## Neural Network
        nnIcon = QIcon('icons/nn.png')
        self.classTypeComboBox.addItem(nnIcon, 'Neural Network')
        nnPage = QWidget()
        self.paramStack.addWidget(nnPage)

        # fields
        self.nnNumHiddenUnitsSpinBox = self.__setSpinBox(0, 0, 10, 1, nnPage)
        self.nnActivationComboBox = QComboBox(nnPage)
        self.nnActivationComboBox.addItem('relu')
        self.nnActivationComboBox.addItem('logistic')
        self.nnActivationComboBox.addItem('tanh')
        self.nnActivationComboBox.addItem('identity')
        self.nnBatchSizeLineEdit = QLineEdit('200', nnPage)
        self.nnLearningRateComboBox = QComboBox(nnPage)
        self.nnLearningRateComboBox.addItem('constant')
        self.nnLearningRateComboBox.addItem('invscaling')
        self.nnLearningRateComboBox.addItem('adaptive')
        self.nnLearningRateInitLineEdit = QLineEdit('0.001', nnPage)
        self.nnEarlyStoppingCheckBox = QCheckBox('', nnPage)

        nnStopLabel = QLabel('Stopping Criteria:', nnPage)
        nnTolLabel = QLabel('tol:', nnPage)
        nnTolLabel.setMinimumWidth(60)
        self.nnTolLineEdit = QLineEdit('1e-3', nnPage)
        nnMaxIterLabel = QLabel('max_iter:', nnPage)
        nnMaxIterLabel.setMinimumWidth(60)
        self.nnMaxIterLineEdit = QLineEdit('100', nnPage)

        # layout
        nnLayout = QFormLayout()
        nnLayout.addRow('num_hidden_units:', self.nnNumHiddenUnitsSpinBox)
        nnLayout.addRow('activation:', self.nnActivationComboBox)
        nnLayout.addRow('batch_size:', self.nnBatchSizeLineEdit)
        nnLayout.addRow('learning_rate:', self.nnLearningRateComboBox)
        nnLayout.addRow('learning_rate_init:', self.nnLearningRateInitLineEdit)
        nnLayout.addRow('early_stopping:', self.nnEarlyStoppingCheckBox)

        nnSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        nnStopLayout = QHBoxLayout()
        nnStopLayout.addWidget(nnTolLabel)
        nnStopLayout.addWidget(self.nnTolLineEdit)
        nnStopLayout.addWidget(nnMaxIterLabel)
        nnStopLayout.addWidget(self.nnMaxIterLineEdit)

        nnPageLayout = QVBoxLayout(nnPage)
        nnPageLayout.addLayout(nnLayout)
        nnPageLayout.addItem(nnSpacer)
        nnPageLayout.addWidget(nnStopLabel)
        nnPageLayout.addLayout(nnStopLayout)

        ## SVM
        svmIcon = QIcon('icons/svm.png')
        self.classTypeComboBox.addItem(svmIcon, 'SVM')
        svmPage = QWidget()
        self.paramStack.addWidget(svmPage)

        # fields
        self.svmPenaltyDoubleSpinBox = self.__setDoubleSpinBox(1, 0, 10, 0.1, 1, svmPage)
        self.svmKernelComboBox = QComboBox(svmPage)
        self.svmKernelComboBox.addItem('rbf')
        self.svmKernelComboBox.addItem('linear')
        self.svmKernelComboBox.addItem('polynomial')
        self.svmKernelComboBox.addItem('sigmoid')
        self.svmDegreeSpinBox = self.__setSpinBox(3, 1, 5, 1, svmPage)
        self.svmDegreeSpinBox.setDisabled(True)
        self.svmKernelComboBox.currentIndexChanged.connect(\
            lambda: self.svmDegreeSpinBox.setEnabled(self.svmKernelComboBox.currentIndex() == 2))
        self.svmGammaLineEdit = QLineEdit('', svmPage)
        self.svmKernelComboBox.currentIndexChanged.connect(\
            lambda: self.svmGammaLineEdit.setDisabled(self.svmKernelComboBox.currentIndex() == 1))
        self.svmCoefDoubleSpinBox = self.__setDoubleSpinBox(0, -10, 10, 0.1, 1, svmPage)
        self.svmKernelComboBox.currentIndexChanged.connect(\
            lambda: self.svmCoefDoubleSpinBox.setDisabled(self.svmKernelComboBox.currentIndex() in [0, 1]))
        self.svmClassWeightComboBox = QComboBox(svmPage)
        self.svmClassWeightComboBox.addItem('uniform')
        self.svmClassWeightComboBox.addItem('balanced')

        svmStopLabel = QLabel('Stopping Criteria:', svmPage)
        svmTolLabel = QLabel('tol:', svmPage)
        svmTolLabel.setMinimumWidth(60)
        self.svmTolLineEdit = QLineEdit('1e-3', svmPage)
        svmMaxIterLabel = QLabel('max_iter:', svmPage)
        svmMaxIterLabel.setMinimumWidth(60)
        self.svmMaxIterLineEdit = QLineEdit('100', svmPage)

        # layout
        svmLayout = QFormLayout()
        svmLayout.addRow('penalty:', self.svmPenaltyDoubleSpinBox)
        svmLayout.addRow('kernel:', self.svmKernelComboBox)
        svmLayout.addRow('degree:', self.svmDegreeSpinBox)
        svmLayout.addRow('gamma:', self.svmGammaLineEdit)
        svmLayout.addRow('coef0:', self.svmCoefDoubleSpinBox)
        svmLayout.addRow('class_weight:', self.svmClassWeightComboBox)

        svmSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        svmStopLayout = QHBoxLayout()
        svmStopLayout.addWidget(svmTolLabel)
        svmStopLayout.addWidget(self.svmTolLineEdit)
        svmStopLayout.addWidget(svmMaxIterLabel)
        svmStopLayout.addWidget(self.svmMaxIterLineEdit)

        svmPageLayout = QVBoxLayout(svmPage)
        svmPageLayout.addLayout(svmLayout)
        svmPageLayout.addItem(svmSpacer)
        svmPageLayout.addWidget(svmStopLabel)
        svmPageLayout.addLayout(svmStopLayout)

        ## Naive bayes
        nbIcon = QIcon('icons/nb.png')
        self.classTypeComboBox.addItem(nbIcon, 'Naive Bayes')
        nbPage = QWidget()
        self.paramStack.addWidget(nbPage)

        # fields
        self.nbDistributionLabel = QLabel('')
        self.nbAddSmoothDoubleSpinBox = self.__setDoubleSpinBox(1, 0, 50, 0.5, 1, nbPage)
        self.nbFitPriorCheckBox = QCheckBox(nbPage)
        self.nbFitPriorCheckBox.setChecked(True)
        self.nbClassPriorLineEdit = QLineEdit('None', nbPage)

        nbStopLabel = QLabel('Stopping Criteria:', nbPage)
        nbTolLabel = QLabel('tol:', nbPage)
        nbTolLabel.setMinimumWidth(60)
        self.nbTolLineEdit = QLineEdit('1e-3', nbPage)
        nbMaxIterLabel = QLabel('max_iter:', nbPage)
        nbMaxIterLabel.setMinimumWidth(60)
        self.nbMaxIterLineEdit = QLineEdit('100', nbPage)

        # layout
        nbLayout = QFormLayout()
        nbLayout.addRow('distributon:', self.nbDistributionLabel)
        nbLayout.addRow('add_smooth:', self.nbAddSmoothDoubleSpinBox)
        nbLayout.addRow('fit_prior:', self.nbFitPriorCheckBox)
        nbLayout.addRow('class_prior:', self.nbClassPriorLineEdit)

        nbSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

        nbStopLayout = QHBoxLayout()
        nbStopLayout.addWidget(nbTolLabel)
        nbStopLayout.addWidget(self.nbTolLineEdit)
        nbStopLayout.addWidget(nbMaxIterLabel)
        nbStopLayout.addWidget(self.nbMaxIterLineEdit)

        nbPageLayout = QVBoxLayout(nbPage)
        nbPageLayout.addLayout(nbLayout)
        nbPageLayout.addItem(nbSpacer)
        nbPageLayout.addWidget(nbStopLabel)
        nbPageLayout.addLayout(nbStopLayout)

        ### classifier name
        classNameLabel = self.__setLabel('Classifier Name:', modelPage, titleFont)
        self.classNameLineEdit = QLineEdit(modelPage)
        self.classNameLineEdit.setDisabled(True)
        self.paramStack.currentChanged.connect(\
            lambda: self.classNameLineEdit.setEnabled(self.paramStack.currentIndex() > 0))

        classNameLayout = QHBoxLayout()
        classNameLayout.addWidget(classNameLabel)
        classNameLayout.addWidget(self.classNameLineEdit)

        modelPageLayout.addLayout(classNameLayout)

        ### comment
        classCommentLabel = self.__setLabel('Comment:', modelPage, titleFont)
        self.classCommentTextEdit = QTextEdit(modelPage)
        self.classCommentTextEdit.setMaximumHeight(50)
        self.classCommentTextEdit.setDisabled(True)
        self.paramStack.currentChanged.connect(\
            lambda: self.classCommentTextEdit.setEnabled(self.paramStack.currentIndex() > 0))

        modelPageLayout.addWidget(classCommentLabel)
        modelPageLayout.addWidget(self.classCommentTextEdit)

        ### reset and train buttons
        classResetTrainSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        classResetPushButton = QPushButton('Reset', modelPage)
        classResetPushButton.setMinimumWidth(90)
        classResetPushButton.setDisabled(True)
        self.paramStack.currentChanged.connect(\
            lambda: classResetPushButton.setEnabled(self.paramStack.currentIndex() > 0))
        classTrainPushButton = QPushButton('Train', modelPage)
        classTrainPushButton.setMinimumWidth(90)
        classTrainPushButton.setDefault(True)
        classTrainPushButton.setDisabled(True)
        self.paramStack.currentChanged.connect(\
            lambda: classTrainPushButton.setEnabled(self.paramStack.currentIndex() > 0))
        classTrainPushButton.clicked.connect(self.__trainClassifier)

        classResetTrainLayout = QHBoxLayout()
        classResetTrainLayout.addItem(classResetTrainSpacer)
        classResetTrainLayout.addWidget(classResetPushButton)
        classResetTrainLayout.addWidget(classTrainPushButton)

        modelPageLayout.addLayout(classResetTrainLayout)

        ### page spacer and line
        modelPageSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        modelPageLayout.addItem(modelPageSpacer)
        modelLine = QFrame(modelPage)
        modelLine.setFrameShape(QFrame.HLine)
        modelLine.setFrameShadow(QFrame.Sunken)
        modelPageLayout.addWidget(modelLine)

        ### back and next buttons
        classBackNextSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        classBackPushButton = QPushButton('Back', modelPage)
        classBackPushButton.setMinimumWidth(90)
        classBackPushButton.clicked.connect(lambda: self.leftPanel.setCurrentIndex(0))
        classNextPushButton = QPushButton('Next', modelPage)
        classNextPushButton.setMinimumWidth(90)
        classNextPushButton.setDefault(True)
        classNextPushButton.setDisabled(True)
        classTrainPushButton.clicked.connect(lambda: classNextPushButton.setEnabled(True))
        classNextPushButton.clicked.connect(lambda: self.leftPanel.setCurrentIndex(2))

        classBackNextLayout = QHBoxLayout()
        classBackNextLayout.addItem(classBackNextSpacer)
        classBackNextLayout.addWidget(classBackPushButton)
        classBackNextLayout.addWidget(classNextPushButton)

        modelPageLayout.addLayout(classBackNextLayout)

        self.leftPanel.addWidget(modelPage)


        ########## 3rd page: model selection and testing ##########
        testPage = QWidget()
        testPageLayout = QVBoxLayout(testPage)

        ### classifier selection
        classSelectLabel = self.__setLabel('Classifier Selection:', testPage, titleFont)
        testPageLayout.addWidget(classSelectLabel)

        classSelectFrame = QFrame(testPage)
        classSelectFrame.setAutoFillBackground(True)
        classSelectLayout = QVBoxLayout(classSelectFrame)
        bestPerformRadioButton = QRadioButton('Best-Performing', classSelectFrame)
        bestPerformRadioButton.setChecked(True)
        userPickRadioButton = QRadioButton('User-Picked', classSelectFrame)
        bestPerformSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        metricLabel = QLabel('Metric:', classSelectFrame)
        metricComboBox = QComboBox(classSelectFrame)
        metricComboBox.addItem('accuracy')
        metricComboBox.addItem('precision')
        metricComboBox.addItem('recall')
        metricComboBox.addItem('f1')
        metricComboBox.addItem('AUROC')
        metricComboBox.addItem('AUPRC')
        bestPerformRadioButton.toggled.connect(metricComboBox.setEnabled)
        userPickRadioButton.toggled.connect(metricComboBox.setDisabled)
        userPickLabel = QLabel('<classifierName>', classSelectFrame)
        userPickLabel.setMinimumWidth(150)

        bestPerformLayout = QHBoxLayout()
        bestPerformLayout.addWidget(bestPerformRadioButton)
        bestPerformLayout.addItem(bestPerformSpacer)
        bestPerformLayout.addWidget(metricLabel)
        bestPerformLayout.addWidget(metricComboBox)
        classSelectLayout.addLayout(bestPerformLayout)

        userPickLayout = QHBoxLayout()
        userPickLayout.addWidget(userPickRadioButton)
        userPickLayout.addWidget(userPickLabel)
        classSelectLayout.addLayout(userPickLayout)

        testPageLayout.addWidget(classSelectFrame)

        ### test button
        testPushButton = QPushButton('Test')
        testPushButton.setMinimumWidth(90)
        testPushButton.setDefault(True)
        testSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        testLayout = QHBoxLayout()
        testLayout.addItem(testSpacer)
        testLayout.addWidget(testPushButton)
        testPageLayout.addLayout(testLayout)

        ### test result
        testResultLabel = self.__setLabel('Test Result:', testPage, titleFont)
        testResultList = QListView(testPage)
        testResultList.setMinimumHeight(250)
        testPageLayout.addWidget(testResultLabel)
        testPageLayout.addWidget(testResultList)

        ### prediction button
        predictionLabel = self.__setLabel('Prediction:', testPage, titleFont)
        self.predictionPushButton = QPushButton('Predict and Save As...', testPage)
        self.predictionPushButton.setMaximumWidth(175)
        self.predictionPushButton.setDisabled(True)
        predictionLayout = QHBoxLayout()
        predictionLayout.addWidget(predictionLabel)
        predictionLayout.addWidget(self.predictionPushButton)
        testPageLayout.addLayout(predictionLayout)

        ### page spacer and line
        testPageSpacer = QSpacerItem(40, 20,QSizePolicy.Minimum, QSizePolicy.Expanding)
        testPageLayout.addItem(testPageSpacer)
        testLine = QFrame(testPage)
        testLine.setFrameShape(QFrame.HLine)
        testLine.setFrameShadow(QFrame.Sunken)
        testPageLayout.addWidget(testLine)

        ### back and finish buttons
        testBackPushButton = QPushButton('Back', testPage)
        testBackPushButton.setMinimumWidth(90)
        testBackPushButton.clicked.connect(lambda: self.leftPanel.setCurrentIndex(1))
        testPushButton.clicked.connect(lambda: testBackPushButton.setDisabled(True))
        testFinishPushButton = QPushButton('Finish', testPage)
        testFinishPushButton.setMinimumWidth(90)
        testFinishPushButton.setDefault(True)
        testFinishPushButton.setDisabled(True)
        testPushButton.clicked.connect(lambda: testFinishPushButton.setEnabled(True))
        testBackFinishSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        testBackFinishLayout = QHBoxLayout()
        testBackFinishLayout.addItem(testBackFinishSpacer)
        testBackFinishLayout.addWidget(testBackPushButton)
        testBackFinishLayout.addWidget(testFinishPushButton)
        testPageLayout.addLayout(testBackFinishLayout)

        self.leftPanel.addWidget(testPage)


        ########## right panel ##########
        rightPanelLayout = QVBoxLayout(self.rightPanel)

        ### trained classifiers
        trainedClassifiersLabel = self.__setLabel('Trained Classifiers:', self.rightPanel, titleFont)
        trainedClassifiersList = QListView(self.rightPanel)
        rightPanelLayout.addWidget(trainedClassifiersLabel)
        rightPanelLayout.addWidget(trainedClassifiersList)

        ### visualization panel
        visLayout = QHBoxLayout()
        visListLayout = QVBoxLayout()
        visList = QListView(self.rightPanel)
        visList.setMaximumWidth(245)
        visListLayout.addWidget(visList)

        visFrame = QFrame(self.rightPanel)
        visFrameLayout = QVBoxLayout(visFrame)
        dataPlotRadioButton = QRadioButton('Data Plot', visFrame)
        rocRadioButton = QRadioButton('ROC', visFrame)
        confusionMatrixRadioButton = QRadioButton('Confusion Matrix', visFrame)
        prRadioButton = QRadioButton('Precision-Recall', visFrame)
        
        visFrameLeftLayout = QVBoxLayout()
        visFrameLeftLayout.addWidget(dataPlotRadioButton)
        visFrameLeftLayout.addWidget(rocRadioButton)
        visFrameRightLayout = QVBoxLayout()
        visFrameRightLayout.addWidget(confusionMatrixRadioButton)
        visFrameRightLayout.addWidget(prRadioButton)
        visFrameTopLayout = QHBoxLayout()
        visFrameTopLayout.addLayout(visFrameLeftLayout)
        visFrameTopLayout.addLayout(visFrameRightLayout)

        visFrameSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        visSavePushButton = QPushButton('Save As...', visFrame)
        saveIcon = QIcon('icons/save.png')
        visSavePushButton.setIcon(saveIcon)
        visFrameBottomLayout = QHBoxLayout()
        visFrameBottomLayout.addItem(visFrameSpacer)
        visFrameBottomLayout.addWidget(visSavePushButton)
        visFrameLayout.addLayout(visFrameTopLayout)
        visFrameLayout.addLayout(visFrameBottomLayout)
        visListLayout.addWidget(visFrame)
        visLayout.addLayout(visListLayout)

        plotArea = QWidget(self.rightPanel)
        plotArea.setFixedSize(340, 340)
        plotArea.setAutoFillBackground(True)
        visLayout.addWidget(plotArea)

        rightPanelLayout.addLayout(visLayout)

        self.resize(1024, 700)
        self.setWindowTitle('ML4Bio')
        self.leftPanel.resize(360, 680)
        self.leftPanel.setStyleSheet("QStackedWidget {background-color:rgb(226, 226, 226)}")
        self.leftPanel.move(10, 10)
        self.rightPanel.resize(640, 680)
        self.rightPanel.move(380, 10)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())