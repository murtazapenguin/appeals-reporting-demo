import { Box, CssBaseline } from "@mui/material";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { useState } from "react";
import { NERViewer } from "./components/NERViewer";
import { PDFViewer } from "./components/PDFViewer";
import {
  comprehensiveNERData,
  sampleBoundingBoxes,
  samplePDFData,
  SearchResults as sampleSearchResults,
} from "./SampleData";

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#4caf50",
    },
  },
  typography: {
    fontFamily:
      'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',
  },
});

function App() {
  const [viewMode, setViewMode] = useState("pdf"); // 'ner' or 'pdf'
  const [searchResults, setSearchResults] = useState(null);

  // NEW: State for managing annotation data
  const [annotationData, setAnnotationData] = useState([]);
  const [showAnnotationStats, setShowAnnotationStats] = useState(false);

  // NEW: State for managing bounding boxes (this will be updated when annotations are saved)
  const [currentBoundingBoxes, setCurrentBoundingBoxes] =
    useState(sampleBoundingBoxes);

  const handleDocumentChange = (documentName) => {
    console.log("Document changed:", documentName);
  };

  const handlePageChange = (pageNumber) => {
    console.log("Page changed:", pageNumber);
  };

  const handleSearchPerformed = async () => {
    // Simulate search API call
    setSearchResults(sampleSearchResults);
  };

  // NEW: Handle when annotations are exported/saved
  const handleAnnotationsSaved = (savedData) => {
    // Update the current bounding boxes with the saved data
    setCurrentBoundingBoxes(savedData);
    setAnnotationData(savedData);
    setShowAnnotationStats(true);

    // Hide stats after 5 seconds
    setTimeout(() => {
      setShowAnnotationStats(false);
    }, 5000);

    // Log the complete annotation data to console in the exact format
    console.log("=== SAVED BOUNDING BOX ANNOTATIONS ===");
    console.log("Total documents with annotations:", savedData.length);
    console.log("Complete annotation data:");
    console.log(JSON.stringify(savedData, null, 2));

    // Also log each document separately for clarity
    savedData.forEach((doc, index) => {
      console.log(`Document ${index + 1}: ${doc.document_name}`);
      console.log(`  - Page: ${doc.page_number}`);
      console.log(`  - Bounding boxes: ${doc.bbox.length}`);
      console.log(`  - Bbox data:`, doc.bbox);
    });

    console.log("=== END ANNOTATION DATA ===");

    // Here you could send the data to your backend
    // Example: await saveAnnotationsToBackend(savedData);
  };

  // NEW: Handle annotation area selection (for ICD mode - existing functionality)
  const handleAreaSelected = (areaData) => {
    console.log("Area selected:", areaData);
    // Handle ICD area selection if needed
  };

  // User interface configuration for PDF viewer
  const pdfUserInterfaces = {
    docNavigation: false,
    zoom: false,
    download: false,
    keyboardShortcuts: true, // Enable to show annotation shortcuts
    showFilename: false,
    enableToolbar: true,
    enableSearch: true,
  };

  // User interface configuration for NER viewer
  const nerUserInterfaces = {
    docNavigation: false,
    zoom: false,
    download: false,
    keyboardShortcuts: false,
    showFilename: false,
  };

  const getAnnotationStats = () => {
    if (!annotationData.length) return null;

    const totalBoxes = annotationData.reduce(
      (total, doc) => total + doc.bbox.length,
      0
    );
    const totalDocs = annotationData.length;

    return { totalBoxes, totalDocs };
  };

  const stats = getAnnotationStats();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: "100vh", bgcolor: "#f5f5f5" }}>
        <Box
          sx={{
            height: "100vh",
            bgcolor: "white",
            overflow: "hidden",
          }}
        >
          {/* Header with Mode Toggle */}
          <div className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode("pdf")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    viewMode === "pdf"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  PDF Viewer with Annotations
                </button>
                <button
                  onClick={() => setViewMode("ner")}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    viewMode === "ner"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  NER Viewer
                </button>
              </div>

              {/* NEW: Show annotation stats when available */}
              {showAnnotationStats && stats && (
                <div className="bg-green-50 border border-green-200 rounded-lg px-4 py-2">
                  <div className="flex items-center gap-2">
                    <span className="text-green-600 font-medium">
                      ✅ Saved!
                    </span>
                    <span className="text-green-700 text-sm">
                      {stats.totalBoxes} bounding boxes across {stats.totalDocs}{" "}
                      documents
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {viewMode === "ner" ? (
            <NERViewer
              documentData={samplePDFData}
              nerData={comprehensiveNERData}
              userInterfaces={nerUserInterfaces}
              onDocumentChange={handleDocumentChange}
              onPageChange={handlePageChange}
            />
          ) : (
            <PDFViewer
              documentData={samplePDFData}
              boundingBoxes={currentBoundingBoxes} // Use the dynamic state
              searchResults={searchResults}
              userInterfaces={pdfUserInterfaces}
              onDocumentChange={handleDocumentChange}
              onPageChange={handlePageChange}
              onSearchPerformed={handleSearchPerformed}
              setSearchResults={setSearchResults}
              // Annotation props
              onAreaSelected={handleAreaSelected}
              onAnnotationAdd={handleAnnotationsSaved}
            />
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
