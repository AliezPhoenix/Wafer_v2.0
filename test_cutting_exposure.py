"""切痕检查临时曝光：读原值、设置、丢弃缓冲帧、只恢复当前相机。"""
import unittest

from Functions import capture_with_temp_exposure, restore_exposure


class FakeCam:
    def __init__(self, exposure=1000.0, images=None, set_ret=0, get_ret=0):
        self.exposure = exposure
        self.images = list(images if images is not None else ["f0", "f1", "f2", "f3"])
        self.set_calls = []
        self.get_image_calls = 0
        self.set_ret = set_ret
        self.get_ret = get_ret

    def Get_parameter(self, parameter_type=None):
        if self.get_ret != 0:
            return self.get_ret, "get fail", None
        return 0, "ok", float(self.exposure)

    def Set_parameter(self, value=0, parameter_type=None):
        self.set_calls.append((float(value), parameter_type))
        if self.set_ret == 0:
            self.exposure = float(value)
        return self.set_ret, "Success" if self.set_ret == 0 else "set fail"

    def Get_image(self):
        self.get_image_calls += 1
        if not self.images:
            return None
        return self.images.pop(0)


class TestCaptureWithTempExposure(unittest.TestCase):
    def test_happy_path_discards_buffered_frames(self):
        cam = FakeCam()
        ret, msg, image, old = capture_with_temp_exposure(cam, 27000, discard_frames=2)
        self.assertEqual(ret, 0)
        self.assertEqual(old, 1000.0)
        self.assertEqual(image, "f2")
        self.assertEqual(cam.get_image_calls, 3)
        self.assertEqual(cam.set_calls[0], (27000.0, "ExposureTime"))

    def test_get_failure_does_not_set_or_grab(self):
        cam = FakeCam(get_ret=7)
        ret, msg, image, old = capture_with_temp_exposure(cam, 27000)
        self.assertEqual(ret, 7)
        self.assertIsNone(image)
        self.assertIsNone(old)
        self.assertEqual(cam.set_calls, [])
        self.assertEqual(cam.get_image_calls, 0)

    def test_set_failure_returns_old_exposure_without_grab(self):
        cam = FakeCam(set_ret=3)
        ret, msg, image, old = capture_with_temp_exposure(cam, 27000)
        self.assertEqual(ret, 3)
        self.assertIsNone(image)
        self.assertEqual(old, 1000.0)
        self.assertEqual(cam.get_image_calls, 0)

    def test_none_image_still_returns_old_exposure(self):
        cam = FakeCam(images=[])
        ret, msg, image, old = capture_with_temp_exposure(cam, 27000, discard_frames=0)
        self.assertNotEqual(ret, 0)
        self.assertIsNone(image)
        self.assertEqual(old, 1000.0)


class TestRestoreExposure(unittest.TestCase):
    def test_restore_only_given_camera(self):
        cam_a = FakeCam(exposure=27000)
        cam_b = FakeCam(exposure=8000)
        ret, _ = restore_exposure(cam_a, 1000.0)
        self.assertEqual(ret, 0)
        self.assertEqual(cam_a.exposure, 1000.0)
        self.assertEqual(cam_b.exposure, 8000.0)
        self.assertEqual(cam_b.set_calls, [])


if __name__ == "__main__":
    unittest.main()
