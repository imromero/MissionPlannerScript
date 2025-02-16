import tkinter as tk
import xml.etree.ElementTree as ET
import logging
from ConfigLoader import ConfigLoader

class ConfigEditorFrame(tk.Frame):
    """
    A Tkinter frame for editing configuration parameters using the ConfigLoader.
    This editor reads and writes configuration parameters directly through the ConfigLoader class.
    Each parameter is displayed with its current (default) value (in parentheses) as part of the label.
    When new values are applied, the configuration is updated and the labels refresh accordingly.
    """
    def __init__(self, parent, missionPlanner, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.mp_ = missionPlanner
        # Use the shared configuration instance from missionPlanner.
        self.config = self.mp_.config_
        # Save original values as defaults
        self.defaultValues = {}
        for param in ["udpIpRec_", "udpIpMeta_", "mavlinkConnection_",
                      "portSendMeta_", "portRecMeta_", "portRecTouch_", "portRecJoystick_", "portRecTemperature_", "txPortVideoApp_",
                      "mode_",
                      "gain_", "pitchNeutral_", "yawNeutral_", "pwmPitchMin_", "pwmPitchMax_", "pwmYawMin_", "pwmYawMax_",
                      "channelPitch_", "channelYaw_", "channelCam_", "channelDeploy1_", "channelDeploy2_",
                      "id_", "token_", "exponentialFactor_"]:
            self.defaultValues[param] = getattr(self.config, param, "")
        
        # Define the parameters to display; keys must match the attribute names in ConfigLoader.
        self.parameters = [
            ("udpIpRec_", "Receiver IP"),
            ("udpIpMeta_", "Meta IP"),
            ("mavlinkConnection_", "MAVLink Connection"),
            ("portSendMeta_", "Send Meta Port"),
            ("portRecMeta_", "Receive Meta Port"),
            ("portRecTouch_", "Touch Port"),
            ("portRecJoystick_", "Joystick Port"),
            ("portRecTemperature_", "Temperature Port"),
            ("txPortVideoApp_", "VideoApp TX Port"),
            ("mode_", "Joystick Mode"),
            ("gain_", "Gimbal Gain"),
            ("pitchNeutral_", "Neutral Pitch"),
            ("yawNeutral_", "Neutral Yaw"),
            ("pwmPitchMin_", "Min PWM Pitch"),
            ("pwmPitchMax_", "Max PWM Pitch"),
            ("pwmYawMin_", "Min PWM Yaw"),
            ("pwmYawMax_", "Max PWM Yaw"),
            ("channelPitch_", "Pitch Channel"),
            ("channelYaw_", "Yaw Channel"),
            ("channelCam_", "Camera Channel"),
            ("channelDeploy1_", "Deploy1 Channel"),
            ("channelDeploy2_", "Deploy2 Channel"),
            ("id_", "Drone ID"),
            ("token_", "Token"),
            ("exponentialFactor_", "Exponential Factor")
        ]
        
        self.entries = {}  # Map each parameter to its Entry widget.
        self.labels = {}   # Map each parameter to its Label widget.
        
        row = 0
        for param, displayName in self.parameters:
            frame = tk.Frame(self)
            frame.grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            default_value = self.defaultValues.get(param, "")
            label_text = f"{displayName} (Current: {default_value})"
            label = tk.Label(frame, text=label_text, font=("Helvetica", 10), anchor="w")
            label.pack(side="left")
            self.labels[param] = label
            
            entry = tk.Entry(frame, width=40)
            entry.pack(side="left", padx=10)
            self.entries[param] = entry
            row += 1
        
        btnFrame = tk.Frame(self)
        btnFrame.grid(row=row, column=0, pady=10)
        btnReset = tk.Button(btnFrame, text="Undo", command=self.ResetFields)
        btnReset.pack(side="left", padx=10)
        btnApply = tk.Button(btnFrame, text="Apply", command=self.ApplyChanges)
        btnApply.pack(side="left", padx=10)
        
        self.ResetFields()

    def ResetFields(self):
        """
        Resets each entry field to the default configuration value (from the XML)
        and updates the label to show the current value.
        """
        for param, displayName in self.parameters:
            default_value = getattr(self.config, param, "")
            self.entries[param].delete(0, tk.END)
            self.entries[param].insert(0, str(default_value))
            label_text = f"{displayName} (Current: {default_value})"
            self.labels[param].config(text=label_text)
            self.defaultValues[param] = default_value

    def ApplyChanges(self):
        """
        Reads new values from the entry fields, updates the configuration object directly,
        writes the new configuration to the XML file via ConfigLoader, reloads the configuration,
        and updates the displayed default values.
        """
        try:
            # Update configuration attributes based on entry values.
            for param, _ in self.parameters:
                new_value = self.entries[param].get().strip()
                default_value = self.defaultValues.get(param, "")
                # Determine the type based on the default value.
                if isinstance(default_value, int):
                    setattr(self.config, param, int(new_value))
                elif isinstance(default_value, float):
                    setattr(self.config, param, float(new_value))
                else:
                    setattr(self.config, param, new_value)
            
            # Write the updated configuration to the XML file.
            self.config.write_config()
            
            # Reload configuration from file.
            newConfig = ConfigLoader(self.config.filePath)
            self.mp_.ApplyNewConfig(newConfig)
            self.config = newConfig
            for param in self.defaultValues:
                self.defaultValues[param] = getattr(self.config, param, "")
            self.ResetFields()
            logging.info("Configuration applied successfully.")
        except Exception as e:
            logging.error("Error applying configuration changes: %s", e)
