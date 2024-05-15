import busio
import board
import adafruit_tpa2016

class SpeakerController():
  def __init__(self, config: dict):
    self.i2c = busio.I2C(board.SCL, board.SDA)
    self.tpa = adafruit_tpa2016.TPA2016(self.i2c)
      
  def toggle_amplifier(self):
    if self.tpa.amplifier_shutdown == True:
      self.tpa.amplifier_shutdown = False
    else:
      self.tpa.amplifier_shutdown = True

  def toggle_speaker(self):
    if (self.tpa.speaker_enable_r == True) and (self.tpa.speaker_enable_l == True):
      self.tpa.speaker_enable_l = False
      self.tpa.speaker_enable_r = False
    else:
      self.tpa.speaker_enable_l = True
      self.tpa.speaker_enable_r = True
  
  def set_attack_time(self, attack_time: int):
    assert attack_time >= 1 and attack_time <= 63, "Invalid attack time (must be between values 1~63)"
    self.tpa.attack_time = attack_time
  
  def set_compression_ratio(self, compression_ratio):
    """
    Set the compression ratio for the speaker controller.

    Parameters:
    compression_ratio (float): The compression ratio to be set. Default set to tpa.COMPRESSION_4_1

    Returns:
    None
    """
    self.tpa.compression_ratio = compression_ratio
  
  def set_fixed_gain(self, fixed_gain: int):
    if self.tpa.compression_ratio == self.tpa.COMPRESSION_1_1:
      assert fixed_gain >= 0 and fixed_gain <= 30, "Compression disable. Invalid fixed gain (must be between values 0~30)"
    else:
      assert fixed_gain >= -28 and fixed_gain <= 30, "Compression enabled. Invalid fixed gain (must be between values -28~24)"
    self.tpa.fixed_gain = fixed_gain
  
  def set_hold_time(self, hold_time: int):
    assert hold_time >= 1 and hold_time <= 63, "Invalid hold time (must be between values 1~63)"
    self.tpa.hold_time = hold_time
  
  def set_max_gain(self, max_gain: int):
    assert max_gain >= 18 and max_gain <= 30, "Invalid max gain (must be between values 18~30)"
    self.tpa.max_gain = max_gain

  def toggle_noise_gate(self):
    """
    NoiseGate function enable. Enabled by default. Can only be enabled when compression ratio is NOT 1:1. To disable, set to False.
    """
    if not self.tpa.noise_gate_enable:
      assert self.tpa.compression_ratio is not self.tpa.COMPRESSION_1_1, "Cannot enable noise gate when compression ratio is 1:1"
      self.tpa.noise_gate_enable = True
    else:
      self.tpa.noise_gate_enable = False
  
  def set_noise_gate_threshold(self, noise_gate_threshold):
    """
    Noise Gate threshold in mV.

    Noise gate settings are 1mV, 4mV, 10mV, and 20mV. 
    Settings options are NOISE_GATE_1, NOISE_GATE_4, NOISE_GATE_10, NOISE_GATE_20. 
    Only functional when compression ratio is NOT 1:1. Defaults to 4mV.
    """
    assert self.tpa.compression_ratio is not self.tpa.COMPRESSION_1_1, "Cannot set noise gate threshold when compression ratio is 1:1"
    assert noise_gate_threshold in [self.tpa.NOISE_GATE_1, self.tpa.NOISE_GATE_4, self.tpa.NOISE_GATE_10, self.tpa.NOISE_GATE_20], "Invalid noise gate threshold"
    self.tpa.noise_gate_threshold = noise_gate_threshold
  
  def disable_output_limiter(self):
    """
    Output limiter disable.

    Enabled by default when compression ratio is NOT 1:1. 
    Can only be disabled if compression ratio is 1:1.
    """
    assert self.tpa.compression_ratio is self.tpa.COMPRESSION_1_1, "Cannot disable output limiter when compression ratio is NOT 1:1"
    self.tpa.output_limiter_disable = True
  
  def set_output_limiter_level(self, level: float):
    """
    The output limiter level in dBV. 
    
    Must be between -6.5 and 9, set in increments of 0.5.
    """
    assert level >= -6.5 and level <= 9, "Invalid output limiter level (must be between values -6.5~9)"
    self.tpa.output_limiter_level = level
  
  def set_release_time(self, release_time: int):
    """
    The release time. 
    
    This is the minimum time between gain increases.
    Set to 1 - 63 where 1 = 0.0137ms, and the time increases 0.0137ms with each step, for a maximum of 0.8631ms. 
    Defaults to 11, or 0.1507ms.
    """
    assert release_time >= 1 and release_time <= 63, "Invalid release time (must be between values 1~63)"
    self.tpa.release_time = release_time
  
  def reset(self):
    if self.tpa.reset_Fault_l == True:
      self.tpa.reset_Fault_l = False
    if self.tpa.reset_fault_r == True:
      self.tpa.reset_fault_r = False
    if self.tpa.reset_thermal == True:
      self.tpa.reset_thermal = False


speaker_controller = SpeakerController({})
