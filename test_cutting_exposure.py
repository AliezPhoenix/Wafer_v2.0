"""高倍曝光：启动默认值、开关切换、切痕临时设置后的恢复。"""
import unittest

from Functions import apply_exposure, cam_params, sync_high_exposure


class FakeCam:
    def __init__(self, exposure=1000.0, frame_rate=60.0, images=None, set_ret=0, get_ret=0):
        self.exposure = exposure
        self.frame_rate = frame_rate
        self.fps_enable = False
        self.images = list(images if images is not None else ["f0", "f1", "f2", "f3"])
        self.set_calls = []
        self.get_image_calls = 0
        self.set_ret = set_ret
        self.get_ret = get_ret

    def Get_parameter(self, parameter_type=None):
        if self.get_ret != 0:
            return self.get_ret, "get fail", None
        if parameter_type == "AcquisitionFrameRate":
            return 0, "ok", float(self.frame_rate)
        return 0, "ok", float(self.exposure)

    def Set_parameter(self, value=0, parameter_type=None):
        if parameter_type == "AcquisitionFrameRateEnable":
            self.fps_enable = bool(value)
            self.set_calls.append((bool(value), parameter_type))
            return 0, "Success"
        self.set_calls.append((float(value), parameter_type))
        if self.set_ret != 0 and parameter_type == "ExposureTime":
            return self.set_ret, "set fail"
        if parameter_type == "ExposureTime":
            self.exposure = float(value)
        elif parameter_type == "AcquisitionFrameRate":
            self.frame_rate = float(value)
        return 0, "Success"

    def Get_image(self):
        self.get_image_calls += 1
        if not self.images:
            return None
        return self.images.pop(0)


class TestApplyExposure(unittest.TestCase):
    def test_set_number(self):
        cam = FakeCam()
        apply_exposure(cam, 27000)
        self.assertEqual(cam.exposure, 27000.0)

    def test_restore_dict_and_fps(self):
        cam = FakeCam(exposure=27000, frame_rate=15)
        apply_exposure(cam, {"ExposureTime": 1000.0, "AcquisitionFrameRate": 60.0})
        self.assertEqual(cam.exposure, 1000.0)
        self.assertEqual(cam.frame_rate, 60.0)
        self.assertTrue(cam.fps_enable)

    def test_restore_only_one_cam(self):
        a, b = FakeCam(exposure=27000), FakeCam(exposure=8000)
        apply_exposure(a, {"ExposureTime": 1000.0, "AcquisitionFrameRate": 60.0})
        self.assertEqual(a.exposure, 1000.0)
        self.assertEqual(b.exposure, 8000.0)

    def test_discard(self):
        cam = FakeCam(images=["a", "b"])
        apply_exposure(cam, 1000.0, discard=2)
        self.assertEqual(cam.get_image_calls, 2)

    def test_cam_params(self):
        self.assertEqual(
            cam_params(FakeCam(exposure=5000, frame_rate=40)),
            {"ExposureTime": 5000.0, "AcquisitionFrameRate": 40.0},
        )


class TestSyncHighExposure(unittest.TestCase):
    def setUp(self):
        self.c1, self.c2 = FakeCam(), FakeCam(exposure=8000)
        self.cams = {1: self.c1, 2: self.c2}
        self.defaults = {1: cam_params(self.c1), 2: cam_params(self.c2)}

    def test_on_sets_current(self):
        sync_high_exposure(self.cams, self.defaults, 1, 0, 1, 1, 2)
        self.assertEqual(self.c1.exposure, 27000.0)

    def test_off_restores(self):
        self.c1.exposure = 27000
        sync_high_exposure(self.cams, self.defaults, 0, 1, 1, 1, 2)
        self.assertEqual(self.c1.exposure, 1000.0)

    def test_cam_change(self):
        self.c1.exposure = 27000
        sync_high_exposure(self.cams, self.defaults, 1, 1, 2, 1, 2)
        self.assertEqual(self.c1.exposure, 1000.0)
        self.assertEqual(self.c2.exposure, 27000.0)

    def test_level_zero_or_low_mag(self):
        sync_high_exposure(self.cams, self.defaults, 1, 0, 1, 1, 0)
        self.assertEqual(self.c1.exposure, 1000.0)
        sync_high_exposure(self.cams, self.defaults, 1, 0, 0, 0, 2)
        self.assertEqual(self.c1.exposure, 1000.0)


if __name__ == "__main__":
    unittest.main()
