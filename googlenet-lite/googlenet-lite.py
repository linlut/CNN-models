"""
GoogLeNet-lite (Inception) model for CIFAR-10 image recognition.

Inspired by:
    Deep Learning Specialization at Coursera
    http://dandxy89.github.io/ImageModels/googlenet/#info

GoogLeNet architecture adapted for CIFAR-10 dataset classification. Original paper:
    https://arxiv.org/pdf/1409.4842.pdf

Karolis M. December 2017.
"""


from helpers import *
from keras.layers import *
from keras.models import Model
from keras import optimizers
from keras.preprocessing.image import ImageDataGenerator


# Data preparation
download_and_extract_data()
x_train, _, y_train= load_training_data()
x_test, _, y_test = load_test_data()
input_shape = list(x_train.shape[1:])
classes = y_train.shape[1]



# Inception module
def inception_module(X, filter_sizes):

    # 1x1 covolution
    conv_1x1 = Conv2D(filter_sizes[0], kernel_size=1, strides=1, padding='same', use_bias=False, activation='relu')(X)

    # Bottleneck layer and 3x3 convolution
    conv_3x3 = Conv2D(filter_sizes[1], kernel_size=1, strides=1, padding='same', use_bias=False, activation='relu')(X)
    conv_3x3 = Conv2D(filter_sizes[2], kernel_size=3, strides=1, padding='same', use_bias=False, activation='relu')(conv_3x3)

    # Bottleneck layer and 5x5 convolution
    conv_5x5 = Conv2D(filter_sizes[3], kernel_size=1, strides=1, padding='same', use_bias=False, activation='relu')(X)
    conv_5x5 = Conv2D(filter_sizes[4], kernel_size=5, strides=1, padding='same', use_bias=False, activation='relu')(conv_5x5)

    # Max pooling and bottleneck layer
    max_pool = MaxPooling2D(pool_size=3, strides=1, padding='same')(X)
    max_pool = Conv2D(filter_sizes[5], kernel_size=1, strides=1, padding='same', use_bias=False, activation='relu')(max_pool)

    # Concatenate all tensors to 1 tensor
    X = concatenate([conv_1x1, conv_3x3, conv_5x5, max_pool], axis=3)

    return X



# Full model
def create_model(input_shape, classes):

    # TODO: add auxiliary classifiers to model

    # Define the input
    X_input = Input(input_shape)

    # Stage 1 - layers before inception modules
    X = Conv2D(filters=32, kernel_size=5, strides=1, padding='same', use_bias=False, activation='relu')(X_input)
    X = MaxPooling2D(pool_size=3, strides=2, padding='same')(X)
    X = BatchNormalization(axis=3)(X)
    X = Conv2D(filters=32, kernel_size=1, strides=1, padding='valid', use_bias=False, activation='relu')(X)
    X = Conv2D(filters=96, kernel_size=3, strides=1, padding='same', use_bias=False, activation='relu')(X)
    X = BatchNormalization(axis=3)(X)
    X = MaxPooling2D(pool_size=3, strides=1, padding='same')(X)

    # Stage 2 - 2 inception modules and max pooling
    X = inception_module(X, filter_sizes=[32, 48, 64, 8, 16, 16])
    X = inception_module(X, filter_sizes=[64, 64, 96, 16, 48, 32])
    X = MaxPooling2D(pool_size=3, strides=2, padding='same')(X)

    # Stage 3 - 5 inception modules and max pooling
    X = inception_module(X, filter_sizes=[96, 48, 104, 8, 24, 32])
    X = inception_module(X, filter_sizes=[80, 56, 112, 12, 32, 32])
    X = inception_module(X, filter_sizes=[64, 64, 128, 12, 32, 32])
    X = inception_module(X, filter_sizes=[56, 72, 144, 16, 32, 32])
    X = inception_module(X, filter_sizes=[128, 80, 160, 16, 64, 64])
    X = MaxPooling2D(pool_size=3, strides=2, padding='same')(X)

    # Stage 4 - 2 inception modules and average pooling
    X = inception_module(X, filter_sizes=[128, 80, 160, 16, 64, 64])
    X = inception_module(X, filter_sizes=[192, 96, 192, 24, 64, 64])
    X = AveragePooling2D(pool_size=4, strides=1, padding='valid')(X)

    # Stage 5 - dropout, linear fc, softmax fc
    X = Flatten()(X)
    X = Dropout(0.4)(X)
    X = Dense(classes, activation='linear')(X)
    X = Dense(classes, activation='softmax')(X)

    # Create model
    model = Model(inputs=X_input, outputs=X)

    return model


# Define optimizer and compile model
optimizer = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
GoogLeNet = create_model(input_shape=input_shape, classes=classes)
GoogLeNet.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics = ['accuracy'])


# Generator for data augmantation
datagen = ImageDataGenerator(
        rotation_range=30,  # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=True)  # randomly flip images


# Train model
results = GoogLeNet.fit_generator(datagen.flow(x_train, y_train,
                                 batch_size = 250),
                                 epochs = 100,
                                 steps_per_epoch=200,  # data_size/batch size
                                 validation_data=(x_test, y_test))


# Plot train / validation results
plot_results(results)


# Print model architecture
GoogLeNet.summary()