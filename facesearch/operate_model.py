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

class FileHandler():
    def import_dataset(self, source: Path, target: Path, reset=False) -> None:
        """
            Imports image from source to target

            Args:
                souce   : Where the images are from.
                target  : Where the images will be imported to.
                reset   : If set to true, will delete everything in the target directory.

            Expected source tree:
            ```
                source
                  ├── person_1
                  │     ├── image_1.jpg
                  │     ├── ...
                  │     └── image_100.jpg
                  |   ...
                  └── person_100
                        ├── image_1.jpg
                        ├── ...
                        └── image_100.jpg
            ```

            Returns: None
        """

        total_files = len([file for file in source.rglob('*') if file.is_file()])
        progbar = tf.keras.utils.Progbar(total_files, unit_name="files")

        if not target.exists():
            target.mkdir(exist_ok=True)

        if reset:
            self.reset_directory(target)

        for person in source.iterdir():
            if person.is_file():
                continue

            person_id = self.generate_random_string(4)

            for image_path in person.iterdir():
                if image_path.is_dir():
                    continue

                image_path = str(image_path)

                image_id = self.generate_random_string(8)

                image_name = f"{person_id}_{image_id}.jpg"

                target_path = target.joinpath(image_name)

                self.save_image(image_path, target_path)

                progbar.add(1)

    def save_image(self, image:str|np.ndarray|Path, target:str|Path) -> bool:
        """
            Saves an image into target path

            Args:
                image   : The image itself. Can be a string path, a numpy array of pixel values, or a pathlib.Path object.
                target  : Where the images will be saved.
                reset   : If set to true, will delete everything in the target directory.

            Returns: True if saved else False

            Example:
                >>> import cv2
                >>> from pathlib import Path
                >>> fh = FileHandler()
                >>> image = cv2.imread("image.jpg")
                >>> target_path = Path("folder_name")
                >>> fh.save_image(image, target_path)
                True
        """

        # Converts string path into a pathlib.Path object.
        # This is used to check if parent folder exists.
        if isinstance(target, str):
            target = Path(target)

        # Creates parent folders if they don't exist.
        if not target.parent.parent.exists():
            target.parent.parent.mkdir(exist_ok=True)

        if not target.parent.exists():
            target.parent.mkdir(exist_ok=True)

        target = str(target)

        # OpenCV cannot create a copy of an image if the image is a path and not an array of pixel values.
        # And so, we use OpenCV to read the image so that we can pass the image and create a copy of it.
        if isinstance(image, str):
            image = cv2.imread(image)

        saved = cv2.imwrite(target, image)

        return True if saved else False

    def generate_random_string(self, output_n:int) -> str:
        """
            Generates random string in output_n times.

            Args:
                output_n: How many strings will the output be.

            Returns: Generated string
        """

        characters      = string.ascii_letters + string.digits
        random_string   = ''.join(rd.choice(characters) for _ in range(output_n))

        return random_string

    def reset_directory(self, target:Path|str) -> None:
        """
            Resets a given directory.

            Args:
                target: The target directory. Can be a pathlib.Path object or a string.

            Returns: None
        """

        if isinstance(target, str):
            match (target):
                case "anchor":
                    target = ANC_DATASET_PATH

                case "negative":
                    target = NEG_DATASET_PATH

                case "positive":
                    target = POS_DATASET_PATH

                case "raw":
                    target = RAW_DATASET_PATH

                case "processed":
                    target = PROC_DATASET_PATH

                case "augmented":
                    target = AUG_DATASET_PATH

                case "dataset":
                    target = DATASET_PATH

        if not target.exists():
            return

        for path in target.iterdir():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    def save_triplet(self, triplet:list[str]) -> bool:
        """
            Saves a triplet.

            Args:
                triplet: A list of stringed path of each: anchor, positive, negative images.

            Returns: True if sucessful else false.
        """

        anc_path, pos_path, neg_path  = triplet

        # Create pathlib.Path objects.
        anc = Path(anc_path)
        pos = Path(pos_path)
        neg = Path(neg_path)

        # Read images.
        img_anc = cv2.imread(anc_path)
        img_pos = cv2.imread(pos_path)
        img_neg = cv2.imread(neg_path)

        # For naming format.
        # This is important to avoid duplicates causing errors.
        triplet_id = self.generate_random_string(8)

        anc_image_id = self.generate_random_string(4)
        pos_image_id = self.generate_random_string(4)
        neg_image_id = self.generate_random_string(4)

        anc_is_saved = self.save_image(img_anc, ANC_DATASET_PATH.joinpath(triplet_id + "_" + anc_image_id + anc.suffix))
        pos_is_saved = self.save_image(img_pos, POS_DATASET_PATH.joinpath(triplet_id + "_" + pos_image_id + pos.suffix))
        neg_is_saved = self.save_image(img_neg, NEG_DATASET_PATH.joinpath(triplet_id + "_" + neg_image_id + neg.suffix))

        return anc_is_saved and pos_is_saved and neg_is_saved

    def save_triplets(self, triplets:list[str]) -> None:
        """
            Saves all generated triplet into each classes' folder.

            Arguments:
                triplets: a list of generated triplets.
        """

        # Just a trustee progressbar for aesthetic lol
        triplets_len = len(triplets)
        save_progbar = tf.keras.utils.Progbar(triplets_len)

        print("\nSaving triplets...")

        for i in range(triplets_len):
            self.save_triplet(triplets[i])

            save_progbar.update(i + 1)

    def select_random_element(self, data_list:list):
        """
            Selects a random element from a given list.

            Arguments:
                data_list: a list.

            Retuns: Randomly selected element from the given list.
        """

        data_list_len   = (len(data_list) - 1)
        random_index    = rd.randint(0, data_list_len)

        element = data_list[random_index]

        return element

    def get_images(self, source:Path, person:Path|None=None, sort:bool=False) -> list[Path]:
        """
            Fetches image from a given source. If person is specified, will fetch images with the same person_id as the given person pathlib.Path object.

            Expected image name format:
                personID_imageID.jpg, 5h43kj_lkj54.jpg, thisperson_lkj54.jpg

            Arguments:
                source  : A pathlib.Path object which the image(s) are from.
                person  : A pathlib.Path object of the person.
                sort    : If true, sorts the fetched image list.

            Retuns: A list of pathlib.Path objects of each images.
        """

        images = None

        if person:
            person_id = person.stem.split("_")[0]

            images = list(source.glob(person_id + "_*.jpg"))
        else:
            images = list(source.glob("*.jpg"))

        if sort:
            images = sorted(images)

        return images

    def open_images(self, image_paths:list[Path], as_gray:bool=False) -> np.ndarray:
        """
            Open images with opencv in a given list of pathlib.Path objects of the images.

            Arguments:
                image_paths : A list of pathlib.Path objects of the images.
                as_gray     : If true, reads images as grayscale reducing its channel size from 3 to 1.

            Retuns: A numpy array image values.
        """

        opened_images = []

        for image_path in image_paths:
            if as_gray:
                image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            else:
                image = cv2.imread(str(image_path))

            opened_images.append(image)

        return np.array(opened_images)