import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from core.config import config

class StorageManager:
    """
    Handles saving extracted data to disk in various formats (Excel, JSON).
    Ensures data is organized by module and extraction date/time.
    """
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.base_dir = config.OUTPUT_BASE_DIR
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _create_output_dir(self) -> str:
        """
        Creates the required directory structure: datos/module_name/YYYYMMDD_HHMMSS/
        
        Returns:
            str: The path to the created directory.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dir_path = os.path.join(self.base_dir, self.module_name, timestamp)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def save_to_excel(self, data: List[Dict[str, Any]], filename: str = "data.xlsx") -> Optional[str]:
        """
        Saves a list of dictionaries to an Excel file.
        """
        if not data:
            self.logger.warning("No data provided to save.")
            return None
            
        try:
            output_dir = self._create_output_dir()
            file_path = os.path.join(output_dir, filename)
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            
            self.logger.info(f"Data successfully saved to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to save data to Excel: {e}")
            return None

    def save_to_json(self, data: List[Dict[str, Any]], filename: str = "data.json") -> Optional[str]:
        """
        Saves a list of dictionaries to a JSON file.
        """
        if not data:
            self.logger.warning("No data provided to save.")
            return None
            
        try:
            output_dir = self._create_output_dir()
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
            self.logger.info(f"Data successfully saved to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to save data to JSON: {e}")
            return None

    def save(self, data: List[Dict[str, Any]], format_type: Optional[str] = None) -> Optional[str]:
        """
        Generic save method based on configuration or passed parameter.
        """
        fmt = format_type or config.DEFAULT_FORMAT
        if fmt.lower() == "excel":
            return self.save_to_excel(data)
        elif fmt.lower() == "json":
            return self.save_to_json(data)
        else:
            self.logger.error(f"Unsupported format: {fmt}")
            return None
