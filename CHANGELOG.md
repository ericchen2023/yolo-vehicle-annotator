# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-language support (English, Japanese)
- Video annotation support
- Custom model training pipeline
- Cloud backup integration

## [2.1.3] - 2025-08-26

### Added
- 🧠 **YOLOv8 Model Selection System**
  - Interactive model selection dialog with five YOLOv8 variants (nano, small, medium, large, extra-large)
  - Detailed model information cards showing performance metrics, file sizes, and use cases
  - Automatic model download functionality with progress tracking
  - Responsive dialog design that adapts to different screen sizes
  - Model validation and input verification
  - Integration with AI assistant for seamless model switching

### Changed
- 🎯 **Enhanced Export Precision**
  - Improved annotation coordinate precision from 6 to 12 decimal places in YOLO format
  - Enhanced JSON format with 12-decimal precision for all coordinate values
  - Updated COCO format with high-precision coordinate handling
  - Added precision testing suite to verify export accuracy

### Technical Details
- **Model Selection**: Five YOLOv8 variants available with automatic download and hardware-based recommendations
- **Export Precision**: YOLO format outputs coordinates with `.12f` precision, JSON/COCO formats apply `round(value, 12)`
- **User Interface**: Responsive model selection dialog accessible via F4 shortcut key
- **AI Integration**: Seamless model switching integrated with AI assistant functionality

## [2.1.2] - 2025-08-19

### Changed
- 🔧 **Export System Fixes**
  - Unified all YOLO exports to `exports/yolo/` directory
  - Automatic directory creation during export process
  - Fixed annotation format conversion issues for accurate export files
  - Improved error handling and messaging in export process

### Fixed
- Fixed `[Errno 2] No such file or directory: 'labels\test2.txt'` error
- Corrected empty export file issues
- Resolved inconsistent export path problems

## [2.1.1] - 2025-08-19

### Changed
- 🔧 **Code Structure Optimization**
  - Removed redundant files and consolidated related functionality
  - Integrated yolo_exporter.py functionality into advanced_exporter.py
  - Cleaned up duplicate import statements across all modules
  - Optimized project file structure from 23 to 20 core files

- 📊 **Performance Improvements**
  - Reduced memory usage by removing unnecessary module imports
  - Improved application startup time through import optimization
  - Enhanced code maintainability with clearer module separation
  - Implemented automatic __pycache__ cleanup mechanism

### Fixed
- Fixed duplicate QFileDialog imports in vehicle_class_manager.py (4 instances)
- Corrected duplicate AdvancedExporter import in main.py
- Removed redundant QPixmap import in internal functions
- Resolved import statement redundancies across modules

### Removed
- Deleted yolo_exporter.py (functionality merged into advanced_exporter.py)
- Cleaned up __pycache__ directories and compiled Python files
- Removed duplicate import statements throughout the codebase

## [2.1.0] - 2025-08-19

### Added
- 🚗 **Custom Vehicle Class Management System**
  - Complete vehicle type customization beyond fixed categories
  - Professional vehicle class management dialog
  - Dynamic vehicle class creation, editing, and deletion
  - Custom attributes: name, color, emoji, shortcut keys, descriptions

- 📋 **Template System**
  - Pre-defined vehicle class templates (Basic, Detailed, Transport, Commercial)
  - Quick template application for different use cases
  - Template import/export functionality

- 📁 **Import/Export Features**
  - JSON configuration file support for vehicle classes
  - YOLO classes.txt file import/export
  - Cross-project vehicle class settings sharing

- 🎨 **Visual Enhancements**
  - Emoji-based vehicle type visualization
  - Custom color system for each vehicle type
  - Real-time annotation interface updates
  - Improved vehicle class selection UI

### Changed
- Breakthrough fixed vehicle type limitations
- Enhanced annotation interface with custom vehicle types
- Improved user workflow with customizable shortcuts
- Better visual feedback with emoji and color coding

## [2.0.0] - 2025-08-18

### Added
- 🤖 **AI Auto-annotation System**
  - YOLOv8 integration for automatic vehicle detection
  - Batch AI processing with progress tracking
  - AI settings dialog with confidence threshold adjustment
  - Prediction review interface for quality control

- 🎯 **Advanced Annotation Tools**
  - Eight-handle precise editor for pixel-level adjustment
  - Vehicle type quick switching (1-4 keys)
  - Smart bounding box optimization
  - Annotation copying and batch operations

- 📤 **Multi-format Export System**
  - YOLO format (YOLOv8 standard)
  - COCO format (JSON structure)
  - Pascal VOC format (XML structure)
  - Custom JSON format with metadata
  - Batch export with progress tracking

- ⚡ **Performance Optimization**
  - Smart image caching system with LRU algorithm
  - Large image loading optimization
  - Memory monitoring and management
  - Background image preloading

- 💼 **Project Management**
  - Recent files list with quick access
  - Project save/load functionality
  - Automatic backup mechanism
  - User settings persistence

- 🎨 **Modern UI/UX**
  - Dark theme with professional styling
  - Comprehensive toolbar system
  - Complete keyboard shortcuts
  - Responsive layout design
  - Status bar with real-time information

- 🔧 **System Tools**
  - Memory usage monitoring (F8)
  - Cache management interface (F7)
  - Performance optimization tools
  - Error logging and recovery

### Changed
- **Complete UI Redesign**: Modern dark theme with improved usability
- **Enhanced Navigation**: Full keyboard support and intuitive controls
- **Improved Performance**: 3x faster loading for large images
- **Better Error Handling**: Comprehensive error recovery mechanisms

### Fixed
- Delete key behavior now properly deletes selected annotations
- Memory leaks in large image processing
- Annotation precision issues with high-resolution images
- Theme manager dependency removed to eliminate import errors

### Removed
- Theme manager functionality (simplified to single modern theme)
- Unused dependencies and legacy code
- Redundant UI elements

## [1.2.0] - 2025-07-15

### Added
- Basic project management system
- Recent files functionality
- Automatic backup feature
- Settings persistence

### Changed
- Improved annotation accuracy
- Enhanced user interface responsiveness
- Better error messages

### Fixed
- Image loading issues with certain formats
- Annotation save mechanism reliability

## [1.1.0] - 2025-06-20

### Added
- Basic AI assistance (experimental)
- Batch export functionality
- Zoom and navigation controls
- Multiple vehicle class support

### Changed
- Improved image display quality
- Enhanced annotation tools

### Fixed
- Image path handling on Windows
- Annotation coordinate calculations

## [1.0.0] - 2025-05-10

### Added
- Initial release
- Basic annotation functionality
- YOLO format export
- Vehicle classification (4 types)
- Simple image navigation
- Basic UI with essential tools

### Features
- Manual bounding box annotation
- Vehicle type selection
- Single image processing
- Basic YOLO format output

---

## Version Support

| Version | Status | End of Support |
|---------|--------|----------------|
| 2.0.x   | ✅ Active | TBD |
| 1.2.x   | 🔧 Maintenance | 2025-12-31 |
| 1.1.x   | ❌ End of Life | 2025-06-30 |
| 1.0.x   | ❌ End of Life | 2025-05-31 |

## Migration Guide

### From v1.x to v2.0
1. **Backup your projects** before upgrading
2. **Update dependencies**: `pip install -r requirements.txt`
3. **Configuration migration**: Settings will be automatically migrated
4. **New features**: AI functionality requires YOLOv8 models (auto-downloaded)

### Breaking Changes in v2.0
- Theme manager removed (automatic migration to modern theme)
- Configuration file format updated
- Some keyboard shortcuts changed (see documentation)

---

*For detailed technical changes, see the [commit history](https://github.com/ericchen2023/yolo-vehicle-annotator/commits/main).*
