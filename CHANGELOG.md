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
