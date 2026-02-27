import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnnotationToolbar } from "./AnnotationToolbar";
import { ConfirmationDialog } from "./ConfirmationDialog";
import { PDFPageRenderer } from "./PDFPageRenderer";
import { PDFToolbar } from "./PDFToolbar";

export const PDFViewer = ({
  documentData,
  boundingBoxes = null,
  searchResults = null,
  onDocumentChange,
  onPageChange,
  onAnnotationAdd,
  onSearchPerformed,
  className = "",
  setSearchResults,
  userInterfaces,
  isAddingICD = false,
  onAreaSelected,
}) => {
  const [currentFile, setCurrentFile] = useState(documentData.files[0]);
  const [currentPage, setCurrentPage] = useState(1);
  const [zoom, setZoom] = useState(1);
  const [annotationMode, setAnnotationMode] = useState("none");
  const [annotations, setAnnotations] = useState([]);
  const [annotationHistory, setAnnotationHistory] = useState([[]]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [visiblePageInCenter, setVisiblePageInCenter] = useState(1);
  const [selectedRegion, setSelectedRegion] = useState(null);

  // NEW: Enhanced annotation state for multiple bounding boxes
  const [drawnAnnotations, setDrawnAnnotations] = useState([]); // Current drawn annotations
  const [annotationHistoryStack, setAnnotationHistoryStack] = useState([[]]); // History for undo/redo
  const [annotationHistoryIndex, setAnnotationHistoryIndex] = useState(0);
  const [savedAnnotations, setSavedAnnotations] = useState([]); // Final saved annotations

  // NEW: Track deleted existing bounding boxes
  const [deletedExistingBboxes, setDeletedExistingBboxes] = useState(new Set());
  const [existingBboxHistory, setExistingBboxHistory] = useState([new Set()]);
  const [existingBboxHistoryIndex, setExistingBboxHistoryIndex] = useState(0);

  // NEW: Dialog state management
  const [confirmDialog, setConfirmDialog] = useState({
    open: false,
    title: "",
    message: "",
    onConfirm: null,
    severity: "warning",
  });

  // NEW: Unsaved changes warning state
  const [unsavedChangesDialog, setUnsavedChangesDialog] = useState({
    open: false,
    pendingAction: null,
  });

  // Loading states
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isSearchLoading, setIsSearchLoading] = useState(false);
  const [preloadedImages, setPreloadedImages] = useState(new Map());
  const [preloadingProgress, setPreloadingProgress] = useState(0);
  const [isPreloading, setIsPreloading] = useState(false);
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");
  const [currentSearchIndex, setCurrentSearchIndex] = useState(-1);
  const [showNoResults, setShowNoResults] = useState(false);

  // Scroll and navigation refs
  const contentRef = useRef(null);
  const pageRefs = useRef({});
  const observerRef = useRef(null);
  const scrollAnimationRef = useRef(null);
  const keyboardIntervalRef = useRef(null);
  const keyboardTimeoutRef = useRef(null);
  const scrollToPageTimeoutRef = useRef(null);

  // Keyboard state management
  const [pressedKeys, setPressedKeys] = useState(new Set());
  const pressedKeysRef = useRef(new Set());

  // Fix Issue #2: Memoize currentFilePages to prevent unnecessary re-renders
  const currentFilePages = useMemo(() => {
    return documentData.presigned_urls[currentFile] || {};
  }, [documentData.presigned_urls, currentFile]);

  const totalPages = Object.keys(currentFilePages).length;
  const pageNumbers = Object.keys(currentFilePages)
    .map(Number)
    .sort((a, b) => a - b);

  // NEW: Get existing bounding boxes for current page (filtered by deleted ones)
  const getCurrentPageExistingBboxes = useMemo(() => {
    if (!boundingBoxes || !Array.isArray(boundingBoxes)) return [];

    return boundingBoxes.filter(
      (bboxGroup) =>
        bboxGroup.document_name === currentFile &&
        parseInt(bboxGroup.page_number) === currentPage
    );
  }, [boundingBoxes, currentFile, currentPage]);

  // NEW: Check if there are unsaved changes
  const hasUnsavedChanges = useMemo(() => {
    return drawnAnnotations.length > 0;
  }, [drawnAnnotations]);

  // NEW: Control annotation toolbar visibility based on enableToolbar prop
  const isAnnotationToolbarEnabled = useMemo(() => {
    return userInterfaces?.enableToolbar === true;
  }, [userInterfaces?.enableToolbar]);

  // 1. Fix getTotalAnnotationCount to count ALL annotations (not just current page)
  const getTotalAnnotationCount = useCallback(() => {
    let existingCount = 0;

    // Count ALL existing bboxes across all pages for current document
    if (boundingBoxes && Array.isArray(boundingBoxes)) {
      boundingBoxes.forEach((bboxGroup) => {
        if (bboxGroup.document_name === currentFile) {
          bboxGroup.bbox.forEach((_, index) => {
            const bboxId = `existing-${bboxGroup.document_name}-${bboxGroup.page_number}-${index}`;
            if (!deletedExistingBboxes.has(bboxId)) {
              existingCount++;
            }
          });
        }
      });
    }

    // Count ALL drawn annotations for current document
    const drawnCount = drawnAnnotations.filter(
      (ann) => ann.document_name === currentFile
    ).length;

    return existingCount + drawnCount;
  }, [
    boundingBoxes, // Use full boundingBoxes instead of getCurrentPageExistingBboxes
    deletedExistingBboxes,
    drawnAnnotations,
    currentFile, // Remove currentPage dependency
  ]);

  // NEW: Function to check for unsaved changes and show warning
  const checkUnsavedChanges = useCallback(
    (pendingAction) => {
      if (hasUnsavedChanges) {
        setUnsavedChangesDialog({
          open: true,
          pendingAction: pendingAction,
        });
        return true; // Has unsaved changes
      }
      return false; // No unsaved changes
    },
    [hasUnsavedChanges]
  );

  // NEW: Handle unsaved changes dialog actions
  const handleUnsavedChangesAction = useCallback(
    (action) => {
      const pendingAction = unsavedChangesDialog.pendingAction;
      setUnsavedChangesDialog({ open: false, pendingAction: null });

      if (action === "save") {
        // Save first, then execute pending action
        performSave();
        if (pendingAction) {
          setTimeout(() => pendingAction(), 100);
        }
      } else if (action === "discard") {
        // Discard changes and execute pending action
        setDrawnAnnotations([]);
        setAnnotationHistoryStack([[]]);
        setAnnotationHistoryIndex(0);
        if (pendingAction) {
          pendingAction();
        }
      }
      // For 'cancel', we just close the dialog and do nothing
    },
    [unsavedChangesDialog.pendingAction]
  );

  // Add escape key handler for ICD mode and annotation mode
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        if (isAddingICD) {
          // Cancel ICD addition mode by dispatching a custom event
          const event = new CustomEvent("cancelICDAddition");
          document.dispatchEvent(event);
        } else if (
          annotationMode === "boundingbox" &&
          isAnnotationToolbarEnabled
        ) {
          // Exit annotation mode only if toolbar is enabled
          setAnnotationMode("none");
        }
      }
    };

    if (
      isAddingICD ||
      (annotationMode === "boundingbox" && isAnnotationToolbarEnabled)
    ) {
      document.addEventListener("keydown", handleKeyDown);
    }

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isAddingICD, annotationMode, isAnnotationToolbarEnabled]);

  // NEW: Add beforeunload event listener for browser navigation
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges && isAnnotationToolbarEnabled) {
        e.preventDefault();
        e.returnValue =
          "You have unsaved bounding box annotations. Are you sure you want to leave without saving?";
        return "You have unsaved bounding box annotations. Are you sure you want to leave without saving?";
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [hasUnsavedChanges, isAnnotationToolbarEnabled]);

  // Image preloading function
  const preloadImages = useCallback(async () => {
    if (!documentData || !documentData.presigned_urls) return;

    setIsPreloading(true);
    const imageMap = new Map();
    const allUrls = [];

    Object.entries(documentData.presigned_urls).forEach(([fileName, pages]) => {
      Object.entries(pages).forEach(([pageNumber, url]) => {
        allUrls.push({ fileName, pageNumber, url });
      });
    });

    const totalImages = allUrls.length;
    let loadedCount = 0;

    const loadPromises = allUrls.map(({ fileName, pageNumber, url }) => {
      return new Promise((resolve) => {
        const img = new Image();

        img.onload = () => {
          imageMap.set(url, img);
          loadedCount++;
          setPreloadingProgress((loadedCount / totalImages) * 100);
          resolve();
        };

        img.onerror = () => {
          console.warn(
            `Failed to preload image: ${fileName} page ${pageNumber}`
          );
          loadedCount++;
          setPreloadingProgress((loadedCount / totalImages) * 100);
          resolve();
        };

        img.src = url;
      });
    });

    try {
      await Promise.all(loadPromises);
      setPreloadedImages(imageMap);
      console.log(`Successfully preloaded ${imageMap.size} images`);
    } catch (error) {
      console.error("Error during image preloading:", error);
    } finally {
      setIsPreloading(false);
    }
  }, [documentData]);

  // Enhanced smooth scroll function with easing
  const smoothScrollTo = useCallback((targetScroll, duration = 300) => {
    if (!contentRef.current) return;

    const container = contentRef.current;
    const startScroll = container.scrollTop;
    const distance = targetScroll - startScroll;

    if (Math.abs(distance) < 5) {
      container.scrollTop = targetScroll;
      return;
    }

    const startTime = performance.now();

    if (scrollAnimationRef.current) {
      cancelAnimationFrame(scrollAnimationRef.current);
    }

    const animateScroll = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Ease-out-cubic
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);

      container.scrollTop = startScroll + distance * easeOutCubic;

      if (progress < 1) {
        scrollAnimationRef.current = requestAnimationFrame(animateScroll);
      } else {
        scrollAnimationRef.current = null;
      }
    };

    scrollAnimationRef.current = requestAnimationFrame(animateScroll);
  }, []);

  // Direct scroll function for continuous keyboard scrolling
  const directScroll = useCallback((scrollAmount) => {
    if (!contentRef.current) return;

    const container = contentRef.current;
    const targetScroll = Math.max(
      0,
      Math.min(
        container.scrollHeight - container.clientHeight,
        container.scrollTop + scrollAmount
      )
    );

    container.scrollTop = targetScroll;
  }, []);

  // Scroll to specific page function
  const scrollToPage = useCallback(
    (pageNumber) => {
      if (!contentRef.current || !pageRefs.current[pageNumber]) return;

      const container = contentRef.current;
      const pageElement = pageRefs.current[pageNumber];

      if (scrollToPageTimeoutRef.current) {
        clearTimeout(scrollToPageTimeoutRef.current);
      }

      const containerRect = container.getBoundingClientRect();
      const pageRect = pageElement.getBoundingClientRect();

      const containerCenter = containerRect.height / 2;
      const pageCenter = pageRect.height / 2;
      const targetOffset =
        pageRect.top - containerRect.top - containerCenter + pageCenter;

      const targetScroll = container.scrollTop + targetOffset;

      smoothScrollTo(targetScroll, 800);

      scrollToPageTimeoutRef.current = setTimeout(() => {
        setVisiblePageInCenter(pageNumber);
        setCurrentPage(pageNumber);
        onPageChange?.(pageNumber);
      }, 850);
    },
    [smoothScrollTo, onPageChange]
  );

  // Set up intersection observer to track visible page
  useEffect(() => {
    if (!contentRef.current) return;

    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    const observer = new IntersectionObserver(
      (entries) => {
        let mostVisiblePage = visiblePageInCenter;
        let highestRatio = 0;

        entries.forEach((entry) => {
          if (
            entry.isIntersecting &&
            entry.intersectionRatio > highestRatio &&
            entry.intersectionRatio >= 0.3
          ) {
            const pageElement = entry.target;
            const pageNumber = parseInt(pageElement.dataset.pageNumber || "1");
            if (!isNaN(pageNumber)) {
              mostVisiblePage = pageNumber;
              highestRatio = entry.intersectionRatio;
            }
          }
        });

        if (mostVisiblePage !== visiblePageInCenter) {
          setVisiblePageInCenter(mostVisiblePage);
          setCurrentPage(mostVisiblePage);
          onPageChange?.(mostVisiblePage);
        }
      },
      {
        root: contentRef.current,
        rootMargin: "-20% 0px -20% 0px",
        threshold: [0.1, 0.3, 0.5, 0.7, 0.9],
      }
    );

    // Observe all page elements
    Object.values(pageRefs.current).forEach((pageElement) => {
      if (pageElement) {
        observer.observe(pageElement);
      }
    });

    observerRef.current = observer;

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [currentFile, visiblePageInCenter, onPageChange]);

  // Handle initial loading and start preloading
  useEffect(() => {
    const initTimer = setTimeout(() => {
      setIsInitialLoading(false);
    }, 1000);

    preloadImages();

    return () => clearTimeout(initTimer);
  }, [preloadImages]);

  // NEW: Enhanced handleFileChange with unsaved changes check
  const handleFileChange = useCallback(
    (file, targetPage = 1) => {
      // Check for unsaved changes before switching files only if toolbar is enabled
      if (
        isAnnotationToolbarEnabled &&
        checkUnsavedChanges(() => {
          // This is the actual file change logic
          setIsTransitioning(true);
          setCurrentFile(file);

          setTimeout(() => {
            setCurrentPage(targetPage);
            setVisiblePageInCenter(targetPage);
            onDocumentChange?.(file);

            setTimeout(() => {
              scrollToPage(targetPage);
              setIsTransitioning(false);
            }, 100);
          }, 100);
        })
      ) {
        return; // User has unsaved changes, dialog is shown
      }

      // No unsaved changes, proceed with file change
      setIsTransitioning(true);
      setCurrentFile(file);

      setTimeout(() => {
        setCurrentPage(targetPage);
        setVisiblePageInCenter(targetPage);
        onDocumentChange?.(file);

        setTimeout(() => {
          scrollToPage(targetPage);
          setIsTransitioning(false);
        }, 100);
      }, 100);
    },
    [
      onDocumentChange,
      scrollToPage,
      checkUnsavedChanges,
      isAnnotationToolbarEnabled,
    ]
  );

  // Fix Issue #1: Auto-navigate to document and page when boundingBoxes data is provided
  useEffect(() => {
    if (
      boundingBoxes &&
      Array.isArray(boundingBoxes) &&
      boundingBoxes.length > 0
    ) {
      const firstBbox = boundingBoxes[0];
      if (firstBbox.document_name && firstBbox.page_number) {
        const targetDocument = firstBbox.document_name;
        const targetPage = parseInt(firstBbox.page_number);

        if (documentData.files.includes(targetDocument)) {
          setCurrentFile(targetDocument);
          setTimeout(() => scrollToPage(targetPage), 100);
          onDocumentChange?.(targetDocument);
        }
      }
    }
  }, [
    boundingBoxes,
    documentData.files,
    onDocumentChange,
    scrollToPage,
    handleFileChange,
  ]);

  // Auto-navigate to first search result when search results change
  useEffect(() => {
    if (searchResults) {
      setIsSearchLoading(false);

      // Check if search returned no results
      if (
        !searchResults.results ||
        searchResults.results.length === 0 ||
        searchResults.total_matches === 0
      ) {
        setShowNoResults(true);
        setCurrentSearchIndex(-1);

        // Auto-hide the no results message after 4 seconds
        const noResultsTimer = setTimeout(() => {
          setShowNoResults(false);
        }, 10000);

        return () => clearTimeout(noResultsTimer);
      } else {
        // Search has results
        setShowNoResults(false);
        const firstResult = searchResults.results[0];
        setCurrentSearchIndex(0);
        const targetPage = parseInt(firstResult.page_number);

        if (firstResult.document_name !== currentFile) {
          handleFileChange(firstResult.document_name, targetPage);
        } else {
          setTimeout(() => scrollToPage(targetPage), 100);
        }
      }
    }
  }, [searchResults, currentFile, handleFileChange, scrollToPage]);

  // Enhanced keyboard navigation
  useEffect(() => {
    pressedKeysRef.current = pressedKeys;
  }, [pressedKeys]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      const activeElement = document.activeElement;
      if (
        activeElement &&
        (activeElement.tagName === "INPUT" ||
          activeElement.tagName === "TEXTAREA" ||
          activeElement.closest('[role="dialog"]') ||
          activeElement.closest(".modal"))
      ) {
        return;
      }

      if (
        ["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End"].includes(
          e.key
        )
      ) {
        e.preventDefault();

        if (isTransitioning) return;

        const wasAlreadyPressed = pressedKeysRef.current.has(e.key);

        setPressedKeys((prev) => new Set([...prev, e.key]));
        pressedKeysRef.current.add(e.key);

        if (!wasAlreadyPressed) {
          handleInitialKeyPress(e);
          startContinuousScrolling(e.key);
        }
      }
    };

    const handleKeyUp = (e) => {
      if (
        ["ArrowUp", "ArrowDown", "PageUp", "PageDown", "Home", "End"].includes(
          e.key
        )
      ) {
        setPressedKeys((prev) => {
          const newSet = new Set(prev);
          newSet.delete(e.key);
          pressedKeysRef.current.delete(e.key);

          if (newSet.size === 0) {
            stopContinuousScrolling();
          }

          return newSet;
        });
      }
    };

    const handleInitialKeyPress = (e) => {
      if (!contentRef.current) return;

      const container = contentRef.current;
      const containerHeight = container.clientHeight;

      let scrollAmount;

      if (e.key === "ArrowUp" || e.key === "ArrowDown") {
        if (e.ctrlKey || e.metaKey) {
          scrollAmount =
            e.key === "ArrowUp"
              ? -container.scrollHeight
              : container.scrollHeight;
        } else if (e.shiftKey) {
          scrollAmount =
            e.key === "ArrowUp"
              ? -containerHeight * 0.8
              : containerHeight * 0.8;
        } else {
          scrollAmount = e.key === "ArrowUp" ? -150 : 150;
        }
      } else if (e.key === "PageUp" || e.key === "PageDown") {
        scrollAmount =
          e.key === "PageUp" ? -containerHeight * 0.9 : containerHeight * 0.9;
      } else if (e.key === "Home" || e.key === "End") {
        scrollAmount =
          e.key === "Home" ? -container.scrollHeight : container.scrollHeight;
      } else {
        return;
      }

      const targetScroll = Math.max(
        0,
        Math.min(
          container.scrollHeight - container.clientHeight,
          container.scrollTop + scrollAmount
        )
      );

      if (e.ctrlKey || e.metaKey || e.key === "Home" || e.key === "End") {
        smoothScrollTo(targetScroll, 800);
      } else if (e.shiftKey || e.key === "PageUp" || e.key === "PageDown") {
        smoothScrollTo(targetScroll, 500);
      } else {
        smoothScrollTo(targetScroll, 300);
      }
    };

    const startContinuousScrolling = (key) => {
      stopContinuousScrolling();

      keyboardTimeoutRef.current = setTimeout(() => {
        keyboardIntervalRef.current = setInterval(() => {
          if (pressedKeysRef.current.has(key) && contentRef.current) {
            let scrollAmount;

            if (key === "ArrowUp") {
              scrollAmount = -80;
            } else if (key === "ArrowDown") {
              scrollAmount = 80;
            } else if (key === "PageUp") {
              scrollAmount = -300;
            } else if (key === "PageDown") {
              scrollAmount = 300;
            } else {
              return;
            }

            directScroll(scrollAmount);
          } else {
            stopContinuousScrolling();
          }
        }, 50);
      }, 300);
    };

    const stopContinuousScrolling = () => {
      if (keyboardIntervalRef.current) {
        clearInterval(keyboardIntervalRef.current);
        keyboardIntervalRef.current = null;
      }
      if (keyboardTimeoutRef.current) {
        clearTimeout(keyboardTimeoutRef.current);
        keyboardTimeoutRef.current = null;
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("keyup", handleKeyUp);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("keyup", handleKeyUp);
      stopContinuousScrolling();
      pressedKeysRef.current.clear();
    };
  }, [isTransitioning, smoothScrollTo, directScroll]);

  // Enhanced mouse wheel handler
  useEffect(() => {
    const handleWheel = (e) => {
      if (!contentRef.current || isTransitioning) return;

      e.preventDefault();

      const container = contentRef.current;
      let scrollAmount = e.deltaY;

      if (e.deltaMode === 0) {
        scrollAmount = e.deltaY * 0.8;
      } else {
        scrollAmount = e.deltaY * 40;
      }

      const targetScroll = Math.max(
        0,
        Math.min(
          container.scrollHeight - container.clientHeight,
          container.scrollTop + scrollAmount
        )
      );

      container.scrollTop = targetScroll;
    };

    const container = contentRef.current;
    if (container) {
      container.addEventListener("wheel", handleWheel, { passive: false });

      return () => {
        container.removeEventListener("wheel", handleWheel);
      };
    }
  }, [isTransitioning]);

  // Scroll to bounding box function
  const scrollToBoundingBox = useCallback(
    (bbox, imageWidth, imageHeight) => {
      if (!contentRef.current || !bbox || bbox.length === 0) return;

      const [x1, y1, x2, y2, x3, y3, x4, y4] = bbox[0];
      const left = Math.min(x1, x2, x3, x4) * imageWidth * zoom;
      const top = Math.min(y1, y2, y3, y4) * imageHeight * zoom;
      const width =
        (Math.max(x1, x2, x3, x4) - Math.min(x1, x2, x3, x4)) *
        imageWidth *
        zoom;
      const height =
        (Math.max(y1, y2, y3, y4) - Math.min(y1, y2, y3, y4)) *
        imageHeight *
        zoom;

      const container = contentRef.current;
      const containerRect = container.getBoundingClientRect();

      const centerX = left + width / 2;
      const centerY = top + height / 2;

      const scrollLeft = centerX - containerRect.width / 2;
      const scrollTop = centerY - containerRect.height / 2;

      container.scrollTo({
        left: Math.max(0, scrollLeft),
        top: Math.max(0, scrollTop),
        behavior: "smooth",
      });
    },
    [zoom]
  );

  // NEW: Enhanced handlePageChange with unsaved changes check
  const handlePageChange = useCallback(
    (page) => {
      if (page >= 1 && page <= totalPages) {
        // Check for unsaved changes before changing pages only if toolbar is enabled
        if (
          isAnnotationToolbarEnabled &&
          checkUnsavedChanges(() => {
            scrollToPage(page);
          })
        ) {
          return; // User has unsaved changes, dialog is shown
        }
        // No unsaved changes, proceed with page change
        scrollToPage(page);
      }
    },
    [totalPages, scrollToPage, checkUnsavedChanges, isAnnotationToolbarEnabled]
  );

  const handleZoomIn = useCallback(() => {
    setZoom((prev) => Math.min(prev + 0.25, 3));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom((prev) => Math.max(prev - 0.25, 0.25));
  }, []);

  const handleDownload = useCallback(async () => {
    const currentPageUrl = currentFilePages[currentPage.toString()];
    if (currentPageUrl) {
      try {
        const response = await fetch(currentPageUrl, {
          mode: "cors",
          credentials: "omit",
        });

        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = `${currentFile.replace(
            /\.[^/.]+$/,
            ""
          )}_page_${currentPage}.png`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } else {
          throw new Error(`HTTP ${response.status}`);
        }
      } catch (error) {
        console.log("Fetch download failed, trying direct download:", error);
        const link = document.createElement("a");
        link.href = currentPageUrl;
        link.download = `${currentFile.replace(
          /\.[^/.]+$/,
          ""
        )}_page_${currentPage}.png`;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  }, [currentFile, currentPage, currentFilePages]);

  const handleAnnotationAdd = useCallback(
    (annotation) => {
      const newAnnotations = [...annotations, annotation];
      setAnnotations(newAnnotations);

      const newHistory = annotationHistory.slice(0, historyIndex + 1);
      newHistory.push(newAnnotations);
      setAnnotationHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);

      onAnnotationAdd?.(annotation);
    },
    [annotations, annotationHistory, historyIndex, onAnnotationAdd]
  );

  // NEW: Add annotation to history
  const addToAnnotationHistory = useCallback(
    (newAnnotations, newDeletedExisting = deletedExistingBboxes) => {
      setAnnotationHistoryStack((prev) => {
        const newHistory = prev.slice(0, annotationHistoryIndex + 1);
        newHistory.push([...newAnnotations]);
        return newHistory;
      });
      setExistingBboxHistory((prev) => {
        const newHistory = prev.slice(0, existingBboxHistoryIndex + 1);
        newHistory.push(new Set(newDeletedExisting));
        return newHistory;
      });
      setAnnotationHistoryIndex((prev) => prev + 1);
      setExistingBboxHistoryIndex((prev) => prev + 1);
    },
    [annotationHistoryIndex, existingBboxHistoryIndex, deletedExistingBboxes]
  );

  // NEW: Handle bounding box creation
  const handleBoundingBoxCreate = useCallback(
    (selectionData) => {
      if (!isAnnotationToolbarEnabled) return; // Don't create if toolbar disabled

      const {
        x_min,
        y_min,
        x_max,
        y_max,
        document: documentName,
        page,
      } = selectionData;

      // Create new annotation
      const newAnnotation = {
        id: `bbox-${Date.now()}-${Math.random()}`,
        document_name: documentName,
        page_number: page,
        bbox: [x_min, y_min, x_max, y_max, x_max, y_min, x_min, y_max], // Rectangle corners
        timestamp: new Date().toISOString(),
      };

      const updatedAnnotations = [...drawnAnnotations, newAnnotation];
      setDrawnAnnotations(updatedAnnotations);
      addToAnnotationHistory(updatedAnnotations);

      console.log("Bounding box created:", newAnnotation);
    },
    [drawnAnnotations, addToAnnotationHistory, isAnnotationToolbarEnabled]
  );

  // NEW: Handle individual annotation deletion
  const handleDeleteAnnotation = useCallback(
    (annotationId) => {
      if (!isAnnotationToolbarEnabled) return; // Don't delete if toolbar disabled

      const updatedAnnotations = drawnAnnotations.filter(
        (ann) => ann.id !== annotationId
      );
      setDrawnAnnotations(updatedAnnotations);
      addToAnnotationHistory(updatedAnnotations);
    },
    [drawnAnnotations, addToAnnotationHistory, isAnnotationToolbarEnabled]
  );

  // NEW: Handle existing bounding box deletion
  const handleDeleteExistingBbox = useCallback(
    (bboxId) => {
      if (!isAnnotationToolbarEnabled) return; // Don't delete if toolbar disabled

      const updatedDeleted = new Set(deletedExistingBboxes);
      updatedDeleted.add(bboxId);
      setDeletedExistingBboxes(updatedDeleted);
      addToAnnotationHistory(drawnAnnotations, updatedDeleted);
    },
    [
      deletedExistingBboxes,
      drawnAnnotations,
      addToAnnotationHistory,
      isAnnotationToolbarEnabled,
    ]
  );

  // NEW: Handle annotation mode change
  const handleAnnotationModeChange = useCallback((mode) => {
    setAnnotationMode(mode);
  }, []);

  // NEW: Save all annotations (existing + newly drawn)
  const handleSaveAnnotations = useCallback(() => {
    if (!isAnnotationToolbarEnabled) return; // Don't save if toolbar disabled

    const totalExistingCount = getCurrentPageExistingBboxes.reduce(
      (count, bboxGroup) => {
        return (
          count +
          bboxGroup.bbox.filter((_, index) => {
            const bboxId = `existing-${bboxGroup.document_name}-${bboxGroup.page_number}-${index}`;
            return !deletedExistingBboxes.has(bboxId);
          }).length
        );
      },
      0
    );

    if (totalExistingCount === 0 && drawnAnnotations.length === 0) {
      setConfirmDialog({
        open: true,
        title: "No Annotations to Save",
        message:
          "There are no annotations to save. Please add some bounding boxes first.",
        onConfirm: () => setConfirmDialog((prev) => ({ ...prev, open: false })),
        severity: "info",
      });
      return;
    }

    const totalSaved = totalExistingCount + drawnAnnotations.length;

    setConfirmDialog({
      open: true,
      title: "Save Annotations",
      message: `Are you sure you want to save ${totalSaved} bounding boxes? This will finalize your annotations.`,
      onConfirm: () => {
        performSave();
        setConfirmDialog((prev) => ({ ...prev, open: false }));
      },
      severity: "info",
    });
  }, [
    boundingBoxes,
    drawnAnnotations,
    deletedExistingBboxes,
    getCurrentPageExistingBboxes,
    isAnnotationToolbarEnabled,
  ]);

  // NEW: Separate function to perform the actual save
  const performSave = useCallback(() => {
    if (!isAnnotationToolbarEnabled) return; // Don't save if toolbar disabled

    // Combine existing (non-deleted) and newly drawn annotations
    const savedData = [];

    // Add existing bounding boxes (filter out deleted ones)
    if (boundingBoxes && Array.isArray(boundingBoxes)) {
      boundingBoxes.forEach((bboxGroup) => {
        const remainingBboxes = bboxGroup.bbox.filter((_, index) => {
          const bboxId = `existing-${bboxGroup.document_name}-${bboxGroup.page_number}-${index}`;
          return !deletedExistingBboxes.has(bboxId);
        });

        if (remainingBboxes.length > 0) {
          savedData.push({
            page_number: bboxGroup.page_number,
            document_name: bboxGroup.document_name,
            bbox: remainingBboxes,
          });
        }
      });
    }

    // Add newly drawn annotations grouped by document and page
    const groupedNewAnnotations = drawnAnnotations.reduce((acc, annotation) => {
      const key = `${annotation.document_name}-${annotation.page_number}`;
      if (!acc[key]) {
        acc[key] = {
          page_number: annotation.page_number,
          document_name: annotation.document_name,
          bbox: [],
        };
      }
      acc[key].bbox.push(annotation.bbox);
      return acc;
    }, {});

    // Merge with existing or add new entries
    Object.values(groupedNewAnnotations).forEach((newGroup) => {
      const existingEntry = savedData.find(
        (entry) =>
          entry.document_name === newGroup.document_name &&
          entry.page_number === newGroup.page_number
      );

      if (existingEntry) {
        existingEntry.bbox.push(...newGroup.bbox);
      } else {
        savedData.push(newGroup);
      }
    });

    setSavedAnnotations(savedData);

    // Call the parent callback with the saved data
    if (onAnnotationAdd) {
      onAnnotationAdd(savedData);
    }

    const totalExistingCountBeforeClear = getCurrentPageExistingBboxes.reduce(
      (count, bboxGroup) => {
        return (
          count +
          bboxGroup.bbox.filter((_, index) => {
            const bboxId = `existing-${bboxGroup.document_name}-${bboxGroup.page_number}-${index}`;
            return !deletedExistingBboxes.has(bboxId);
          }).length
        );
      },
      0
    );

    const drawnCount = drawnAnnotations.length;
    const totalSaved = totalExistingCountBeforeClear + drawnCount;

    // Clear drawn annotations and deleted existing bbox tracking since they're now saved
    setDrawnAnnotations([]);
    setDeletedExistingBboxes(new Set());

    // Reset histories
    setAnnotationHistoryStack([[]]);
    setAnnotationHistoryIndex(0);
    setExistingBboxHistory([new Set()]);
    setExistingBboxHistoryIndex(0);

    console.log("Annotations saved:", savedData);
    console.log(
      `Successfully saved ${totalSaved} bounding boxes (${totalExistingCountBeforeClear} existing + ${drawnCount} newly drawn)`
    );
  }, [
    boundingBoxes,
    drawnAnnotations,
    deletedExistingBboxes,
    getCurrentPageExistingBboxes,
    onAnnotationAdd,
    isAnnotationToolbarEnabled,
  ]);

  // NEW: Clear all annotations (existing + drawn)
  const handleClearAllAnnotations = useCallback(() => {
    if (!isAnnotationToolbarEnabled) return; // Don't clear if toolbar disabled

    const totalCount = getTotalAnnotationCount();
    if (totalCount === 0) return;

    setConfirmDialog({
      open: true,
      title: "Delete All Annotations",
      message: `Are you sure you want to delete all ${totalCount} annotations in this document? This action cannot be undone.`, // Changed from "on this page" to "in this document"
      onConfirm: () => {
        performClearAll();
        setConfirmDialog((prev) => ({ ...prev, open: false }));
      },
      severity: "error",
    });
  }, [getTotalAnnotationCount, isAnnotationToolbarEnabled]);

  // NEW: Separate function to perform the actual clear
  const performClearAll = useCallback(() => {
    if (!isAnnotationToolbarEnabled) return; // Don't clear if toolbar disabled

    // Mark ALL existing bboxes in current document as deleted (not just current page)
    const newDeletedSet = new Set(deletedExistingBboxes);

    if (boundingBoxes && Array.isArray(boundingBoxes)) {
      boundingBoxes.forEach((bboxGroup) => {
        if (bboxGroup.document_name === currentFile) {
          // Only check document, not page
          bboxGroup.bbox.forEach((_, index) => {
            const bboxId = `existing-${bboxGroup.document_name}-${bboxGroup.page_number}-${index}`;
            newDeletedSet.add(bboxId);
          });
        }
      });
    }

    // Clear ALL drawn annotations for current document (not just current page)
    const emptyAnnotations = drawnAnnotations.filter(
      (ann) => ann.document_name !== currentFile // Remove page filter
    );

    setDrawnAnnotations(emptyAnnotations);
    setDeletedExistingBboxes(newDeletedSet);
    addToAnnotationHistory(emptyAnnotations, newDeletedSet);
  }, [
    deletedExistingBboxes,
    boundingBoxes, // Use full boundingBoxes instead of getCurrentPageExistingBboxes
    drawnAnnotations,
    currentFile, // Remove currentPage dependency
    addToAnnotationHistory,
    isAnnotationToolbarEnabled,
  ]);

  // NEW: Undo annotation
  const handleUndo = useCallback(() => {
    if (!isAnnotationToolbarEnabled) return; // Don't undo if toolbar disabled

    if (annotationHistoryIndex > 0) {
      const newIndex = annotationHistoryIndex - 1;
      const newExistingIndex = existingBboxHistoryIndex - 1;

      setAnnotationHistoryIndex(newIndex);
      setExistingBboxHistoryIndex(newExistingIndex);
      setDrawnAnnotations([...annotationHistoryStack[newIndex]]);
      setDeletedExistingBboxes(new Set(existingBboxHistory[newExistingIndex]));
    }
  }, [
    annotationHistoryIndex,
    existingBboxHistoryIndex,
    annotationHistoryStack,
    existingBboxHistory,
    isAnnotationToolbarEnabled,
  ]);

  // NEW: Redo annotation
  const handleRedo = useCallback(() => {
    if (!isAnnotationToolbarEnabled) return; // Don't redo if toolbar disabled

    if (annotationHistoryIndex < annotationHistoryStack.length - 1) {
      const newIndex = annotationHistoryIndex + 1;
      const newExistingIndex = existingBboxHistoryIndex + 1;

      setAnnotationHistoryIndex(newIndex);
      setExistingBboxHistoryIndex(newExistingIndex);
      setDrawnAnnotations([...annotationHistoryStack[newIndex]]);
      setDeletedExistingBboxes(new Set(existingBboxHistory[newExistingIndex]));
    }
  }, [
    annotationHistoryIndex,
    existingBboxHistoryIndex,
    annotationHistoryStack,
    existingBboxHistory,
    isAnnotationToolbarEnabled,
  ]);

  // Search handlers
  const handleSearchChange = useCallback(
    (query) => {
      setSearchQuery(query);
      if (!query.trim()) {
        setCurrentSearchIndex(-1);
        setSearchResults(null);
        setIsSearchLoading(false);
        setShowNoResults(false);
      }
    },
    [setSearchResults]
  );

  const handleSearchSubmit = useCallback(
    (query) => {
      if (query.trim()) {
        setIsSearchLoading(true);
        setShowNoResults(false);
        onSearchPerformed?.(query);
      }
    },
    [onSearchPerformed]
  );

  const handleSearchNavigate = useCallback(
    (direction) => {
      if (!searchResults || !searchResults.results) return;

      const totalMatches = searchResults.total_matches;
      let newIndex = currentSearchIndex;

      if (direction === "next") {
        newIndex = Math.min(currentSearchIndex + 1, totalMatches - 1);
      } else if (direction === "prev") {
        newIndex = Math.max(currentSearchIndex - 1, 0);
      }

      setCurrentSearchIndex(newIndex);

      const currentResult = searchResults.results[newIndex];
      if (currentResult) {
        const targetPage = parseInt(currentResult.page_number);

        if (currentResult.document_name !== currentFile) {
          handleFileChange(currentResult.document_name, targetPage);
        } else {
          scrollToPage(targetPage);
        }
      }
    },
    [
      searchResults,
      currentSearchIndex,
      currentFile,
      handleFileChange,
      scrollToPage,
    ]
  );

  const handleSearchClear = useCallback(() => {
    setSearchQuery("");
    setCurrentSearchIndex(-1);
    setSearchResults(null);
    setIsSearchLoading(false);
    setShowNoResults(false);
  }, [setSearchResults]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case "z":
            e.preventDefault();
            if (e.shiftKey) {
              handleRedo();
            } else {
              handleUndo();
            }
            break;
          case "y":
            e.preventDefault();
            handleRedo();
            break;
          case "=":
          case "+":
            e.preventDefault();
            handleZoomIn();
            break;
          case "-":
            e.preventDefault();
            handleZoomOut();
            break;
          case "f": {
            e.preventDefault();
            const searchInput = document.querySelector(
              'input[placeholder*="Search"]'
            );
            if (searchInput) {
              searchInput.focus();
            }
            break;
          }
          case "b": {
            // NEW: Ctrl+B to toggle bounding box mode only if toolbar is enabled
            if (isAnnotationToolbarEnabled) {
              e.preventDefault();
              handleAnnotationModeChange(
                annotationMode === "boundingbox" ? "none" : "boundingbox"
              );
            }
            break;
          }
        }
      } else {
        switch (e.key) {
          case "ArrowLeft":
            e.preventDefault();
            handlePageChange(currentPage - 1);
            break;
          case "ArrowRight":
            e.preventDefault();
            handlePageChange(currentPage + 1);
            break;
          case "Escape":
            if (isAnnotationToolbarEnabled) {
              setAnnotationMode("none");
            }
            handleSearchClear();
            break;
          case "F3":
            e.preventDefault();
            if (e.shiftKey) {
              handleSearchNavigate("prev");
            } else {
              handleSearchNavigate("next");
            }
            break;
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [
    currentPage,
    handlePageChange,
    handleZoomIn,
    handleZoomOut,
    handleUndo,
    handleRedo,
    handleSearchNavigate,
    handleSearchClear,
    handleAnnotationModeChange,
    annotationMode,
    isAnnotationToolbarEnabled,
  ]);

  // Cleanup animation frames and intervals on unmount
  useEffect(() => {
    return () => {
      if (scrollAnimationRef.current) {
        cancelAnimationFrame(scrollAnimationRef.current);
      }
      if (keyboardIntervalRef.current) {
        clearInterval(keyboardIntervalRef.current);
      }
      if (keyboardTimeoutRef.current) {
        clearTimeout(keyboardTimeoutRef.current);
      }
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      if (scrollToPageTimeoutRef.current) {
        clearTimeout(scrollToPageTimeoutRef.current);
      }
    };
  }, []);

  const containerStyle = {
    height: "100%",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    position: "relative", // Add positioning context for the annotation toolbar
  };

  const contentStyle = {
    flex: 1,
    overflow: "hidden",
    position: "relative",
    background: "#f8f9fa",
  };

  const statusBarStyle = {
    backgroundColor: "white",
    borderTop: "1px solid #e0e0e0",
    padding: "8px 16px",
    position: "relative",
    zIndex: 10,
    flexShrink: 0,
  };

  const statusContentStyle = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    fontSize: "14px",
    color: "#666",
  };

  const initialLoadingStyle = {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 10,
    flexDirection: "column",
    gap: "20px",
  };

  const spinnerStyle = {
    width: "40px",
    height: "40px",
    border: "4px solid #e0e0e0",
    borderTop: "4px solid #1976d2",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
  };

  const progressBarStyle = {
    width: "300px",
    height: "6px",
    backgroundColor: "#e0e0e0",
    borderRadius: "3px",
    overflow: "hidden",
  };

  const progressFillStyle = {
    height: "100%",
    backgroundColor: "#1976d2",
    borderRadius: "3px",
    transition: "width 0.3s ease",
    width: `${preloadingProgress}%`,
  };

  const formatFileName = (fileName) => {
    const parts = fileName.split(".");
    if (parts.length > 1) {
      return parts.slice(0, -1).join(".");
    }
    return fileName;
  };

  // Show initial loading overlay with preloading progress
  if (isInitialLoading || isPreloading) {
    return (
      <div
        style={{ ...containerStyle, position: "relative" }}
        className={className}
      >
        <div style={initialLoadingStyle}>
          <style>
            {`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}
          </style>
          <div style={spinnerStyle}></div>
          <div style={{ textAlign: "center" }}>
            <div
              style={{
                fontSize: "18px",
                color: "#333",
                fontWeight: "600",
                marginBottom: "8px",
              }}
            >
              Loading PDF Viewer...
            </div>
            {isPreloading && (
              <>
                <div
                  style={{
                    fontSize: "14px",
                    color: "#666",
                    marginBottom: "12px",
                  }}
                >
                  Preloading images: {Math.round(preloadingProgress)}%
                </div>
                <div style={progressBarStyle}>
                  <div style={progressFillStyle}></div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle} className={className}>
      {/* Toolbar */}
      <div style={{ position: "relative", zIndex: 10, flexShrink: 0 }}>
        <PDFToolbar
          files={documentData.files}
          currentFile={currentFile}
          currentPage={visiblePageInCenter}
          totalPages={totalPages}
          zoom={zoom}
          onFileChange={handleFileChange}
          onPageChange={handlePageChange}
          onZoomIn={handleZoomIn}
          onZoomOut={handleZoomOut}
          onDownload={handleDownload}
          documentData={documentData}
          searchQuery={searchQuery}
          searchResults={searchResults}
          currentSearchIndex={currentSearchIndex}
          onSearchChange={handleSearchChange}
          onSearchSubmit={handleSearchSubmit}
          onSearchNavigate={handleSearchNavigate}
          onSearchClear={handleSearchClear}
          userInterfaces={userInterfaces}
          isSearchLoading={isSearchLoading}
        />

        {/* No Search Results Message - positioned beside search */}
        {showNoResults && (
          <div
            style={{
              padding: "8px 16px",
              backgroundColor: "#fef3c7",
              borderLeft: "4px solid #f59e0b",
              borderBottom: "1px solid #e5e7eb",
              fontSize: "14px",
              color: "#92400e",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              animation: "slideInFromTop 0.3s ease-out",
            }}
          >
            <span style={{ fontSize: "16px" }}>🔍</span>
            <span>
              No results found for "{searchQuery}" - try different keywords
            </span>
            <button
              onClick={() => setShowNoResults(false)}
              style={{
                marginLeft: "auto",
                background: "none",
                border: "none",
                cursor: "pointer",
                fontSize: "16px",
                color: "#92400e",
                padding: "0",
                display: "flex",
                alignItems: "center",
                opacity: 0.7,
              }}
              onMouseEnter={(e) => (e.target.style.opacity = "1")}
              onMouseLeave={(e) => (e.target.style.opacity = "0.7")}
              title="Dismiss"
            >
              ×
            </button>
          </div>
        )}

        {/* NEW: Unsaved Changes Warning Banner - Only show if toolbar is enabled */}
        {hasUnsavedChanges && isAnnotationToolbarEnabled && (
          <div
            style={{
              padding: "8px 16px",
              backgroundColor: "#fef3c7",
              borderLeft: "4px solid #f59e0b",
              borderBottom: "1px solid #e5e7eb",
              fontSize: "14px",
              color: "#92400e",
              display: "flex",
              alignItems: "center",
              gap: "8px",
              animation: "slideInFromTop 0.3s ease-out",
            }}
          >
            <span style={{ fontSize: "16px" }}>⚠️</span>
            <span>
              You have {drawnAnnotations.length} unsaved bounding box
              {drawnAnnotations.length > 1 ? "es" : ""}. Remember to save your
              changes before navigating away.
            </span>
            <button
              onClick={handleSaveAnnotations}
              style={{
                marginLeft: "auto",
                background: "#f59e0b",
                color: "white",
                border: "none",
                borderRadius: "4px",
                padding: "4px 12px",
                cursor: "pointer",
                fontSize: "12px",
                fontWeight: "bold",
              }}
              onMouseEnter={(e) => (e.target.style.backgroundColor = "#d97706")}
              onMouseLeave={(e) => (e.target.style.backgroundColor = "#f59e0b")}
            >
              Save Now
            </button>
          </div>
        )}
      </div>

      {/* Multi-page PDF Content */}
      <div style={contentStyle}>
        {/* NEW: Floating Annotation Toolbar - positioned relative to this container */}
        <AnnotationToolbar
          annotationMode={annotationMode}
          onAnnotationModeChange={handleAnnotationModeChange}
          onSaveAnnotations={handleSaveAnnotations}
          onClearAnnotations={handleClearAllAnnotations}
          onUndo={handleUndo}
          onRedo={handleRedo}
          canUndo={annotationHistoryIndex > 0}
          canRedo={annotationHistoryIndex < annotationHistoryStack.length - 1}
          annotationCount={getTotalAnnotationCount()}
          isVisible={isAnnotationToolbarEnabled}
          // Region management props
          drawnAnnotations={drawnAnnotations}
          boundingBoxes={boundingBoxes} // Pass full boundingBoxes array
          currentDocument={currentFile}
          selectedRegion={selectedRegion}
          onRegionSelect={(regionId) => {
            setSelectedRegion(regionId);
          }}
          onDeleteSelectedRegion={(regionId) => {
            // Handle individual region deletion
            if (regionId.startsWith("existing-")) {
              handleDeleteExistingBbox(regionId);
            } else {
              handleDeleteAnnotation(regionId);
            }
            // Clear selection after deletion
            setSelectedRegion(null);
          }}
          onScrollToRegion={(region) => {
            // Handle scrolling to region
            if (region.type === "existing") {
              const targetPage = region.page;
              if (targetPage !== currentPage) {
                scrollToPage(targetPage);
              }
            } else {
              const targetPage = region.annotation.page_number;
              if (targetPage !== currentPage) {
                scrollToPage(targetPage);
              }
            }
          }}
          deletedExistingBboxes={deletedExistingBboxes}
        />

        {/* Corner Elements */}
        {/* Filename indicator - Only show if enabled */}
        {userInterfaces?.showFilename && (
          <div
            style={{
              position: "absolute",
              top: "16px",
              left: "16px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                background: "rgba(255, 255, 255, 0.9)",
                backdropFilter: "blur(8px)",
                padding: "8px 12px",
                borderRadius: "8px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                border: "1px solid #e5e7eb",
                transition: "all 0.3s ease",
                opacity: isTransitioning ? 0.5 : 1,
              }}
            >
              <span
                style={{
                  fontSize: "14px",
                  fontWeight: "500",
                  color: "#374151",
                }}
              >
                {formatFileName(currentFile)}
              </span>
            </div>
          </div>
        )}

        {/* ICD Selection Mode Indicator */}
        {isAddingICD && !isTransitioning && (
          <div
            style={{
              position: "absolute",
              top: "16px",
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 20,
            }}
          >
            <div
              style={{
                background: "#2563eb",
                color: "white",
                padding: "8px 16px",
                borderRadius: "8px",
                boxShadow: "0 4px 12px rgba(37, 99, 235, 0.3)",
                border: "1px solid #1d4ed8",
                animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
              }}
            >
              <div
                style={{ display: "flex", alignItems: "center", gap: "8px" }}
              >
                <div
                  style={{
                    width: "8px",
                    height: "8px",
                    backgroundColor: "white",
                    borderRadius: "50%",
                    animation: "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite",
                  }}
                />
                <span style={{ fontSize: "14px", fontWeight: "bold" }}>
                  Highlight on pdf
                </span>
                <span
                  style={{
                    fontSize: "12px",
                    backgroundColor: "#1d4ed8",
                    padding: "4px 8px",
                    borderRadius: "4px",
                    marginLeft: "8px",
                  }}
                >
                  Press ESC to cancel
                </span>
              </div>
            </div>
          </div>
        )}

        {/* NEW: Bounding Box Annotation Mode Indicator - Only show if toolbar is enabled */}
        {annotationMode === "boundingbox" &&
          !isTransitioning &&
          isAnnotationToolbarEnabled && (
            <div
              style={{
                position: "absolute",
                top: "16px",
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 20,
              }}
            >
              <div
                style={{
                  background: "#059669",
                  color: "white",
                  padding: "8px 16px",
                  borderRadius: "8px",
                  boxShadow: "0 4px 12px rgba(5, 150, 105, 0.3)",
                  border: "1px solid #047857",
                  animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                }}
              >
                <div
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  <div
                    style={{
                      width: "8px",
                      height: "8px",
                      backgroundColor: "white",
                      borderRadius: "50%",
                      animation: "ping 1s cubic-bezier(0, 0, 0.2, 1) infinite",
                    }}
                  />
                  <span style={{ fontSize: "14px", fontWeight: "bold" }}>
                    📦 Draw bounding boxes
                  </span>
                  <span
                    style={{
                      fontSize: "12px",
                      backgroundColor: "#047857",
                      padding: "4px 8px",
                      borderRadius: "4px",
                      marginLeft: "8px",
                    }}
                  >
                    Press ESC to cancel • Ctrl+B toggle
                  </span>
                </div>
              </div>
            </div>
          )}

        <div
          style={{
            position: "absolute",
            top: "16px",
            right: "16px",
            zIndex: 10,
          }}
        >
          <div
            style={{
              background: "rgba(255, 255, 255, 0.9)",
              backdropFilter: "blur(8px)",
              padding: "8px 12px",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
              border: "1px solid #e5e7eb",
              transition: "all 0.3s ease",
              opacity: isTransitioning ? 0.5 : 1,
            }}
          >
            <span style={{ fontSize: "14px", color: "#6b7280" }}>Pg</span>
            <span
              style={{
                fontSize: "14px",
                fontWeight: "500",
                color: "#dc2626",
                marginLeft: "4px",
              }}
            >
              {visiblePageInCenter}
            </span>
            <span
              style={{ fontSize: "14px", color: "#6b7280", marginLeft: "4px" }}
            >
              of {totalPages}
            </span>
          </div>
        </div>

        {/* Loading indicator */}
        {!preloadedImages.size && (
          <div
            style={{
              position: "absolute",
              top: "64px",
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 20,
            }}
          >
            <div
              style={{
                background: "#2563eb",
                color: "white",
                padding: "8px 16px",
                borderRadius: "8px",
                boxShadow: "0 4px 12px rgba(37, 99, 235, 0.3)",
                border: "1px solid #1d4ed8",
              }}
            >
              <div
                style={{ display: "flex", alignItems: "center", gap: "8px" }}
              >
                <div
                  style={{
                    width: "16px",
                    height: "16px",
                    border: "2px solid white",
                    borderTop: "2px solid transparent",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite",
                  }}
                ></div>
                <span style={{ fontSize: "14px", fontWeight: "bold" }}>
                  Loading images for smooth scrolling...
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Keyboard shortcuts indicator - Only show if enabled and annotation toolbar enabled */}
        {userInterfaces?.keyboardShortcuts && (
          <div
            style={{
              position: "absolute",
              bottom: "16px",
              right: "16px",
              zIndex: 10,
            }}
          >
            <div
              style={{
                background: "rgba(0, 0, 0, 0.7)",
                color: "white",
                padding: "8px 12px",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            >
              <div style={{ marginBottom: "4px" }}>
                ↑↓ Scroll • Shift+↑↓ Page • Ctrl+↑↓ Top/Bottom
              </div>
              <div style={{ marginBottom: "4px" }}>
                PgUp/PgDn Page • Home/End Document
              </div>
              {isAnnotationToolbarEnabled && (
                <div style={{ marginBottom: "4px" }}>
                  Ctrl+B Annotate • Ctrl+Z Undo • ESC Cancel
                </div>
              )}
              <div style={{ color: "#fbbf24" }}>
                Hold keys for continuous scroll
              </div>
            </div>
          </div>
        )}

        {/* Scrollable PDF Container */}
        <div
          ref={contentRef}
          className={
            (isAddingICD ||
              (annotationMode === "boundingbox" &&
                isAnnotationToolbarEnabled)) &&
            !isTransitioning
              ? "cursor-none"
              : ""
          }
          style={{
            height: "100%",
            overflowY: "auto",
            overflowX: "hidden",
            scrollBehavior: "auto",
            scrollbarWidth: "thin",
            scrollbarColor: "#cbd5e1 #f1f5f9",
            position: "relative",
          }}
        >
          {/* All Pages Container */}
          <div
            style={{
              minHeight: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              padding: "32px 16px",
              gap: "24px",
            }}
          >
            {pageNumbers.map((pageNumber) => {
              const pageUrl = currentFilePages[pageNumber.toString()];
              if (!pageUrl) return null;

              return (
                <div
                  key={pageNumber}
                  ref={(el) => {
                    if (el) {
                      pageRefs.current[pageNumber] = el;
                      el.dataset.pageNumber = pageNumber.toString();
                    }
                  }}
                  style={{
                    background: "white",
                    borderRadius: "12px",
                    overflow: "hidden",
                    transition: "all 0.5s cubic-bezier(0.4, 0, 0.2, 1)",
                    opacity: isTransitioning ? 0.3 : 1,
                    filter: isTransitioning ? "blur(2px)" : "none",
                    transform: `scale(${isTransitioning ? 0.95 : 1})`,
                    outline:
                      pageNumber === visiblePageInCenter
                        ? "2px solid #3b82f6"
                        : "none",
                    outlineOffset:
                      pageNumber === visiblePageInCenter ? "4px" : "0",
                    boxShadow:
                      pageNumber === visiblePageInCenter
                        ? "0 8px 24px rgba(59, 130, 246, 0.2)"
                        : "0 4px 12px rgba(0,0,0,0.15)",
                    maxWidth: "100%",
                    width: "fit-content",
                    position: "relative",
                  }}
                >
                  {/* Page Number Badge */}
                  <div
                    style={{
                      position: "absolute",
                      top: "12px",
                      left: "12px",
                      zIndex: 10,
                    }}
                  >
                    <div
                      style={{
                        padding: "6px 12px",
                        borderRadius: "20px",
                        fontSize: "12px",
                        fontWeight: "bold",
                        transition: "all 0.3s ease",
                        background:
                          pageNumber === visiblePageInCenter
                            ? "#2563eb"
                            : "#1f2937",
                        color: "white",
                        boxShadow:
                          pageNumber === visiblePageInCenter
                            ? "0 4px 12px rgba(37, 99, 235, 0.4)"
                            : "0 2px 8px rgba(0,0,0,0.3)",
                        outline:
                          pageNumber === visiblePageInCenter
                            ? "2px solid #93c5fd"
                            : "none",
                      }}
                    >
                      Page {pageNumber}
                    </div>
                  </div>

                  {/* Page Content */}
                  <div
                    style={{
                      position: "relative",
                      display: "inline-block",
                      transform: `scale(${zoom})`,
                      transformOrigin: "center center",
                    }}
                  >
                    <PDFPageRenderer
                      imageUrl={pageUrl}
                      pageNumber={pageNumber}
                      zoom={1}
                      // boundingBoxes={getCurrentPageExistingBboxes}
                      boundingBoxes={boundingBoxes}
                      currentDocument={currentFile}
                      annotationMode={annotationMode}
                      annotations={annotations}
                      onAnnotationAdd={handleAnnotationAdd}
                      searchResults={searchResults}
                      currentSearchIndex={currentSearchIndex}
                      onScrollToBoundingBox={scrollToBoundingBox}
                      preloadedImages={preloadedImages}
                      isAddingICD={isAddingICD}
                      onAreaSelected={onAreaSelected}
                      isTransitioning={isTransitioning}
                      // Bounding box annotation props
                      isAnnotationMode={
                        annotationMode === "boundingbox" &&
                        isAnnotationToolbarEnabled
                      }
                      onBoundingBoxCreate={handleBoundingBoxCreate}
                      drawnAnnotations={drawnAnnotations}
                      onDeleteAnnotation={handleDeleteAnnotation}
                      // Existing bbox props
                      deletedExistingBboxes={deletedExistingBboxes}
                      onDeleteExistingBbox={handleDeleteExistingBbox}
                      // NEW: Add selectedRegion prop for highlighting
                      selectedRegion={selectedRegion}
                    />
                  </div>
                </div>
              );
            })}

            {/* Spacer for better scrolling */}
            <div style={{ height: "128px" }}></div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div style={statusBarStyle}>
        <div style={statusContentStyle}>
          <span>
            {currentFile} • Page {visiblePageInCenter} of {totalPages} •{" "}
            {Math.round(zoom * 100)}% zoom
            {preloadedImages.size > 0 && (
              <> • {preloadedImages.size} images preloaded</>
            )}
          </span>
          <span></span>{" "}
        </div>
      </div>

      {/* NEW: Confirmation Dialog - Only show if toolbar is enabled */}
      {isAnnotationToolbarEnabled && (
        <ConfirmationDialog
          open={confirmDialog.open}
          title={confirmDialog.title}
          message={confirmDialog.message}
          onConfirm={confirmDialog.onConfirm}
          onCancel={() =>
            setConfirmDialog((prev) => ({ ...prev, open: false }))
          }
          severity={confirmDialog.severity}
          confirmText={confirmDialog.severity === "error" ? "Delete" : "Save"}
          cancelText="Cancel"
        />
      )}

      {/* NEW: Unsaved Changes Dialog - Only show if toolbar is enabled */}
      {isAnnotationToolbarEnabled && (
        <ConfirmationDialog
          open={unsavedChangesDialog.open}
          title="Unsaved Changes"
          message={`You have ${
            drawnAnnotations.length
          } unsaved bounding box annotation${
            drawnAnnotations.length > 1 ? "s" : ""
          }. What would you like to do?`}
          onConfirm={() => handleUnsavedChangesAction("save")}
          onCancel={() => handleUnsavedChangesAction("cancel")}
          severity="warning"
          confirmText="Save & Continue"
          cancelText="Cancel"
          // Add custom action for discarding changes
          additionalActions={[
            {
              text: "Discard Changes",
              onClick: () => handleUnsavedChangesAction("discard"),
              color: "error",
            },
          ]}
        />
      )}

      {/* Add CSS animations */}
      <style jsx>{`
        @keyframes ping {
          75%,
          100% {
            transform: scale(2);
            opacity: 0;
          }
        }
        @keyframes pulse {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
        @keyframes slideInFromTop {
          0% {
            opacity: 0;
            transform: translateY(-10px);
          }
          100% {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .cursor-none {
          cursor: none !important;
        }
        .cursor-none * {
          cursor: none !important;
        }
      `}</style>
    </div>
  );
};
