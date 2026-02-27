import PDFViewerLib from '../lib/pdf-viewer';

const PDFViewer = ({ documentData, boundingBoxes = [], className = "h-full" }) => {
  return (
    <div className={className}>
      <PDFViewerLib
        documentData={documentData}
        boundingBoxes={boundingBoxes}
        className="h-full"
        userInterfaces={{ enableToolbar: false, zoom: true }}
      />
    </div>
  );
};

export default PDFViewer;
