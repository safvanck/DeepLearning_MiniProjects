import tensorflow as tf
from AlexNet_TF2.model import *
from common.tf.utils.base_executor import *

"""
    The Executor class is responsible for the training and testing of the AlexNet paper. It takes the data loaders and
    configuration (properties.py) as the input. This extends the parents class BaseExecutor, which 
    contains many boilerplate reusable methods.  

    This class was written to reduce and simply the lines of reusable codes needed for a functioning 
    CNN.

"""


class Executor(BaseExecutor):
    def __init__(self, version, data_loaders, config):
        super().__init__(data_loaders, config)
        self.version = version

    def build_model(self):
        """
            This function is for instantiating the model, optimizer, learning rate scheduler and loss function.
        """

        # initialize the model
        self.model = AlexNetModel(num_classes=self.NUM_CLASSES)
        # Save model to tensor board
        # self.save_model_to_tensor_board()

        # self.enable_multi_gpu_training()

        # Send the model to GPU

        # Initialize the Optimizer
        # Need to call self.model.model.parameters() as model is an attribute in the Module function.
        self.optimizer = tf.keras.optimizers.SGD(learning_rate=0.1, momentum=0.9, decay=0.0005)

        # Initialize the learning rate scheduler
        # Reduce learning rate when a metric has stopped improving.
        # Models often benefit from reducing the learning rate by a factor of 2-10 once learning stagnates.
        # This scheduler reads a metrics quantity and if no improvement is seen
        # for a ‘patience’ number of epochs, the learning rate is reduced.
        # https://pytorch.org/docs/stable/optim.html?highlight=reducelronplateau#torch.optim.lr_scheduler.ReduceLROnPlateau
        # Here val accuracy has been used as the metric, hence set mode to 'max'
        # self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=5, verbose=False)

        # Define the Loss Function
        # self.criterion = torch.nn.CrossEntropyLoss()

        # Loss Average
        # self.train_loss_hist = AverageLoss()

        # Enable Precision Mode
        # self.enable_precision_mode()

        self.criterion = tf.keras.losses.sparse_categorical_crossentropy
        self.model.compile(optimizer=self.optimizer, loss=self.criterion, metrics=['accuracy'])

    def train(self):
        """
            This function is used for training the network.
        """

        # Build the model
        self.logger.info("Building model ...")
        self.build_model()

        # self.create_checkpoint_folder()

        # Load model from checkpoint if needed
        # start_epoch = self.load_checkpoint()

        # Training Loop
        self.logger.info("Training starting now ...")
        history = self.model.fit(self.train_data_loader, epochs=10, steps_per_epoch=190, validation_data=self.val_data_loader, validation_steps=20)

        """
        for epoch in range(start_epoch, self.EPOCHS + 1):

            # Invoke the pre training operations
            self.pre_training_loop_ops()

            correct = 0
            total = 0
            for i, (images, labels, _) in enumerate(self.train_data_loader):
                images = images.to(self.DEVICE)
                labels = labels.to(self.DEVICE)

                predictions = self.forward_backward_pass(images, labels, epoch, i)

                # Calculate Train Accuracy
                total, correct = self.cal_prediction(predictions, labels, total, correct)

            # Calculate the training accuracy
            train_accuracy = (100 * correct) / total

            # Invoke the post training operations
            self.post_training_loop_ops(epoch, train_accuracy)

            # Scheduler step() function
            self.scheduler.step(self.train_loss_hist.value)

            # Close the progress bar
            self.pbar.close()

        self.tb_writer.close()
        
        """

    def prediction(self):
        self.logger.info("Building model ...")
        self.build_model()

        # Load model from checkpoint
        self.load_checkpoint()

        test_accuracy = self.prediction_accuracy()

        self.logger.info(f"Test Prediction Accuracy is {test_accuracy}")

        return test_accuracy
