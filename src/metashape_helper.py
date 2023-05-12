import os
import shutil
import time
import Metashape

from data.dataset import Dataset
from settings.settings import settings


class MetashapeHelper():
    def __init__(self, dataset: Dataset, window, logger):
        self.dataset   = dataset
        self.window    = window
        self.logger    = logger

        # Create a metashape document
        self.document  = Metashape.Document()

        # Task amounts that need to be done
        self.task_amount = 0
        
        # Create the coordinate system
        self.coordinate_system = Metashape.CoordinateSystem('LOCAL_CS["Local Coordinates (mm)",LOCAL_DATUM["Local Datum",0],UNIT["millimetre",0.001,AUTHORITY["EPSG","1025"]]]')


    def calculate(self):
        # Delete old file
        if os.path.isfile(self.dataset.psx_file_path):
            shutil.rmtree(self.dataset.model_folder_path)
        
        # Create new document
        self.document.save(self.dataset.psx_file_path)
        # Add a chunk and add a coordinate system
        self.document.addChunk()
        self.document.chunk.crs = self.coordinate_system

        # Set the task amount
        self.task_amount = (1 if settings.get('use_smooth') else 0) + 5

        # Add the photos, the cam poses, the f number and image size
        self.addPhotos()
        self.importCameraReferences()
        self.importCameraCalibration()

        # Go through all calculation tasks
        self.matchPhotos()
        self.alignCameras()
        self.optimizeCameras()
        self.buildDepthMaps()
        self.buildModel()
        
        # Smooth model only if the use_smooth settings is True
        if settings.get('use_smooth'):
            self.smoothModel()

        # Close the document -> Remove lock file manually (metashape does not have a good option for this)
        self.close_document()


    def export(self):
        if os.path.isfile(self.dataset.psx_file_path):
            # Load the existing .psx file
            self.document.open(self.dataset.psx_file_path, read_only=False, ignore_lock=False) 

        # Set the task amount
        self.task_amount = 3

        # Go through all export tasks
        self.buildUV()
        self.buildTexture()
        self.exportModel()

        # Close the document -> Remove lock file manually (metashape does not have a good option for this)
        self.close_document()
        
        
    def addPhotos(self):
        # Log the task start
        self.logger.log_task_start("Add Photos")

        # Add all photos
        self.document.chunk.addPhotos(self.dataset.images)

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log("      Finished!")
    

    def importCameraReferences(self):
        # Log the task start
        self.logger.log_task_start("Import Camera Reference")
        
        # Import the references
        self.document.chunk.importReference(
            path   = self.dataset.cam_pos_file_path, 
            format = Metashape.ReferenceFormatCSV,columns = "nxyz[XYZ]",
            delimiter = " ", 
            crs = self.coordinate_system, 
            skip_rows = 1,
            ignore_labels = False,
            create_markers = False
        )
        self.document.chunk.updateTransform()

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log("      Finished!")

    def importCameraCalibration(self):
        # Log the task start
        self.logger.log_task_start("Import Camera Calibration")
        
        # Prepare calibration
        calibration = Metashape.Calibration()
        calibration.f      = self.dataset.f_number
        calibration.width  = self.dataset.image_size[0]
        calibration.height = self.dataset.image_size[1]

        # Apply calibration to all cameras
        for sensor in self.document.chunk.sensors: 
            sensor.user_calib = calibration
        
        # Save the document
        self.document.save()

        # Log task end
        self.logger.log("      Finished!")


    def matchPhotos(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info("Match Photos", 1, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Match Photos")

        # Execute task
        self.document.chunk.matchPhotos(
            downscale = settings.get('depthmap_downscale'),
            generic_preselection     = True,
            reference_preselection   = True,
            filter_stationary_points = True,
            keypoint_limit  = 250000,
            tiepoint_limit  = 250000,
            keep_keypoints  = False,
            guided_matching = False,
            progress=self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def alignCameras(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info("Align Cameras", 2, self.task_amount)

        # Save the start time of the task 
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Align Cameras")

        # Execute task
        self.document.chunk.alignCameras(
            progress=self.window.update_current_dataset_task_progress
        )
        
        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)
    

    def optimizeCameras(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()
        # Update current task name and number labels in window
        self.window.update_task_info("Optimize Cameras", 3, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Optimize Cameras")

        # Execute task
        self.document.chunk.optimizeCameras(
            fit_f  = True,
            fit_cx = False,
            fit_cy = False,
            fit_b1 = False,
            fit_b2 = False,
            fit_k1 = False,
            fit_k2 = False,
            fit_k3 = False,
            fit_k4 = False,
            fit_p1 = False,
            fit_p2 = False,
            fit_corrections     = False,
            adaptive_fitting    = False,
            tiepoint_covariance = False,
            progress=self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def buildDepthMaps(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()
        # Update current task name and number labels in window
        self.window.update_task_info("Build Depthmaps", 4, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Build Depth Maps")

        # Execute task
        self.document.chunk.buildDepthMaps(
            downscale   = 1,
            filter_mode = Metashape.MildFiltering,
            progress=self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def buildModel(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info("Build Model", 5, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Build Model")

        # If there are tweaks calculate the model with tweaks
        if settings.get('use_tweaks') and (len(settings.get('tweaks')) > 0):
            task = Metashape.Tasks.BuildModel()
            for tweak in settings.get('tweaks'):
                task[tweak[0]] = tweak[1]
            task.face_count  = Metashape.HighFaceCount
            task.source_data = Metashape.DepthMapsData
            # Execute task
            task.apply(
                object=self.document.chunk,
                progress=self.window.update_current_dataset_task_progress
            )
        else:
            # Execute task
            self.document.chunk.buildModel(
                face_count  = Metashape.HighFaceCount,
                source_data = Metashape.DepthMapsData,
                progress=self.window.update_current_dataset_task_progress
            )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def smoothModel(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info("Smooth Model", 6, self.task_amount) 

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Smooth Model")

        # Execute task
        self.document.chunk.smoothModel(
            strength       = 1,
            fix_borders    = False,
            preserve_edges = False,
            progress=self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def buildUV(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info('Build UV', 1, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Build UV")

        # Store the image_texture size
        image_texture_size = settings.get('image_texture_size')

        # Execute task
        self.document.chunk.buildUV(
            mapping_mode = Metashape.GenericMapping,
            page_count   = 1,
            texture_size = image_texture_size,
            progress=self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def buildTexture(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info('Build Texture', 2, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Build texture")

        # Execute task
        self.document.chunk.buildTexture(
            texture_size    = settings.get('image_texture_size'),
            ghosting_filter = True,
            progress=self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def exportModel(self):
        # Clear current task progressbar
        self.window.reset_current_dataset_task_progressbar()

        # Update current task name and number labels in window
        self.window.update_task_info('Export Model', 3, self.task_amount)

        # Save the start time of the task
        start_time = time.time()

        # Log the task start
        self.logger.log_task_start("Export model")

        # Execute task
        self.document.chunk.exportModel(
            path            = self.dataset.obj_file_path,
            binary          = True,
            precision       = 6,
            texture_format  = Metashape.ImageFormatPNG,
            save_texture    = True,
            save_uv         = True,
            save_normals    = True,
            save_colors     = True,
            save_alpha      = True,
            colors_rgb_8bit = True,
            format          = Metashape.ModelFormatOBJ,
            crs             = self.coordinate_system,
            progress        = self.window.update_current_dataset_task_progress
        )

        # Save the document
        self.document.save()

        # Log task end
        self.logger.log_task_finish(start_time)


    def close_document(self):
        # Close delete the document
        del self.document

        # Delete the lock file it it exists (this file is used to check if the document is still opened)
        lock_file = os.path.join(self.dataset.model_folder_path, f"{self.dataset.name}.files", "Lock")
        if os.path.exists(lock_file):
            os.remove(lock_file)
