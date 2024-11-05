import numpy as np

class Preprocessing():
    def preprocess_image(self, image_path:str) -> np.ndarray:
        """
            Preprocess images.

            Arguments:
                image_path : The absolute path of the image.

            Retuns: An array image pixel values.
        """

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        image = self.crop_image_center(image)
        image = self.resize_image(image, 105)

        return image

    def preprocess_dataset(self, source: object, target: object, reset: bool = False):
        """
            Preprocess images from source and saves it into the target directory.

            Arguments:
                source  : The directory where images are initially stored.
                target  : The directory to store preprocessed images.
                reset   : if True, resets target directory.
        """

        if reset and target.exists():
            fh.reset_directory(target)

        total_files = len([file for file in source.rglob('*') if file.is_file()])
        progbar = tf.keras.utils.Progbar(total_files, unit_name="images")

        for image in source.iterdir():
            image_name = image.name
            image_path = str(image)

            preprocessed_image = self.preprocess_image(image_path)
            save_path = target.joinpath(image_name)

            res = fh.save_image(image=preprocessed_image, target=save_path)

            progbar.add(1)

    def resize_image(self, image_array: list, new_size: int) -> np.ndarray:
        """
            Resizes image into a specified new size.

            Retuns: A numpy array of the resized image.
        """

        return cv2.resize(image_array, dsize=(new_size, new_size))

    def crop_image_center(self, image_array: list[float]) -> np.ndarray:
        """
            Crops the image from the center.

            Retuns: A numpy array of the cropped image
        """

        height, width = image_array.shape

        # Finding shortest dimension
        new_dimension = min(height, width)

        # Finding the center
        left    = int((width   - new_dimension) / 2)
        top     = int((height  - new_dimension) / 2)
        right   = int((width   + new_dimension) / 2)
        bottom  = int((height  + new_dimension) / 2)

        # Cropping the image
        return image_array[top:bottom, left:right]


    def augmentate_image(self, base_image: list[float], output_n: int) -> list[float]:
        """
            Augmentates image.

            Args:
                base_image  : The image to augmentate.
                output_n    : The number of images that will be generated from the base_image each with different levels of augmentation.

            Retuns: A list of augmentated images (A list of numpy arrays).
        """

        augmented_images = []

        for i in range(output_n):
            base_image = tf.image.stateless_random_brightness(base_image, max_delta=0.02, seed=(1, 2))
            base_image = tf.image.stateless_random_contrast(base_image, lower=0.7, upper=1, seed=(1,3))
            base_image = tf.image.stateless_random_flip_left_right(base_image, seed=(np.random.randint(100), np.random.randint(100)))
            base_image = tf.image.stateless_random_jpeg_quality(base_image, min_jpeg_quality=75, max_jpeg_quality=95,  seed=(np.random.randint(100), np.random.randint(100)))

            augmented_images.append(base_image)

        return augmented_images

    def augment_images_from_dir(self, source: object, target: object, output_n:int, reset:bool=False) -> None:
        """
            Augmentates image.

            Args:
                source  : Source directory.
                target  : Target directory.
                output_n: The number of images that will be generated from an image in the source directory each with different levels of augmentation.
                reset   : If True, resets target directory else False

            Retuns: A list of augmentated images (A list of numpy arrays).
        """

        if reset and target.exists():
            FileHandler().reset_directory(target)

        total_files = len([file for file in source.rglob('*') if file.is_file()])
        progbar = tf.keras.utils.Progbar(total_files, unit_name="images")

        for data in source.iterdir():
            if data.is_dir():
                continue

            base_name = data.stem

            image = self.image_to_tensor(str(data))

            augmented_images = self.augmentate_image(image, output_n)

            progbar.add(1)

            for augmented_image in augmented_images:
                random_characters   = self.generate_random_string(2)
                image_name          = f"{base_name}_{random_characters}.jpg"

                save_path           = target.joinpath(image_name)
                image_array         = augmented_image.numpy()

                FileHandler().save_image(image_array, save_path)


    def image_to_tensor(self, image_path: str, cvt_gray: bool = False) -> list:
        """
            Reads image as tensor.

            Args:
                image_path  : Aboslute image path.
                cvt_gray    : If True, reads image as grayscale.

            Retuns: A tensor.
        """

        byte_img    = tf.io.read_file(image_path)

        if cvt_gray:
            image_array = tf.io.decode_jpeg(byte_img, channels=1)
        else:
            image_array = tf.io.decode_jpeg(byte_img)

        return image_array

    def normalize_dataset(self, dataset: list) -> list:
        """
            Normalizes images of triplets within the given dataset.

            Args:
                dataset: Dataset.

            Retuns: Normalized dataset.
        """

        new_data = []

        progbar = tf.keras.utils.Progbar(len(dataset), unit_name="images")

        for triplet in dataset:
            normalized_triplet = self.normalize_triplet(*triplet)

            new_data.append(normalized_triplet)

            progbar.add(1)

        return new_data

    def normalize_triplet(self, anchor, positive, negative) -> list:
        """
            Normalizes images of given triplets.

            Args:
                anchor      : Anchor tensor.
                positive    : Positive tensor.
                negative    : Negative tensor.

            Retuns: Normalized triplet.
        """

        anchor     = self.normalize_image(anchor)
        positive   = self.normalize_image(positive)
        negative   = self.normalize_image(negative)

        return [anchor, positive, negative]

    def normalize_image(self, image_array: list) -> list:
        """
            Normalizes given images.

            Args:
                image_array : image array.

            Retuns: Normalized image.
        """

        return image_array/ 255.0

    def generate_random_string(self, output_n: int) -> str:
        """
            Duh. Do I need to explain

            Args:
                output_n: Length of the string to be generated.

            Returns: Generated string
        """

        characters      = string.ascii_letters + string.digits
        random_string   = ''.join(rd.choice(characters) for _ in range(output_n))

        return random_string



class DistanceLayer(Layer):
    def __init__(self, **kwargs):
        super().__init__()

    # Similarity calculation
    def call(self, anchor, positive, negative):
        anchor      = tf.convert_to_tensor(anchor)
        positive    = tf.convert_to_tensor(positive)
        negative    = tf.convert_to_tensor(negative)

        ap_distance = tf.reduce_sum(tf.square(anchor - positive), -1)
        an_distance = tf.reduce_sum(tf.square(anchor - negative), -1)

        return (ap_distance, an_distance)