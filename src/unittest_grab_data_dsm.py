import unittest
import subprocess
import grab_data_dsm as gdd

class TestSum(unittest.TestCase):
    def test_get_dsm_files(self):
         test_files=['DSM_604_68_TIF_UTM32-ETRS89.zip',
                     'DSM_604_69_TIF_UTM32-ETRS89.zip']
         ret=gdd.get_dsm_files(files=test_files,outdir=".")
         self.assertEqual(ret,True)
         

if __name__ == '__main__':
    unittest.main()
