// Native macOS PDF review when Poppler is unavailable.
import AppKit
import PDFKit
import Foundation

let args = Array(CommandLine.arguments.dropFirst())
guard args.count >= 2, let document = PDFDocument(url: URL(fileURLWithPath: args[0])) else {
    fatalError("Usage: render_pdf.swift INPUT.pdf OUTPUT_DIRECTORY [page numbers, one-based]")
}
let directory = URL(fileURLWithPath: args[1], isDirectory: true)
try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
let requested = args.count > 2 ? args.dropFirst(2).compactMap { Int($0).map { $0 - 1 } } : Array(0..<document.pageCount)
var records: [[String: Any]] = []
for index in 0..<document.pageCount {
    guard let page = document.page(at: index) else { continue }
    let bounds = page.bounds(for: .mediaBox)
    records.append(["page": index + 1, "width": bounds.width, "height": bounds.height, "text": page.string ?? ""])
    if !requested.contains(index) { continue }
    let scale: CGFloat = 1.5
    let width = Int(ceil(bounds.width * scale)), height = Int(ceil(bounds.height * scale))
    guard let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: width, pixelsHigh: height,
        bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB,
        bytesPerRow: 0, bitsPerPixel: 0), let context = NSGraphicsContext(bitmapImageRep: bitmap) else { fatalError("Bitmap allocation failed") }
    let cg = context.cgContext
    cg.setFillColor(NSColor.white.cgColor)
    cg.fill(CGRect(x: 0, y: 0, width: width, height: height))
    cg.scaleBy(x: scale, y: scale)
    cg.translateBy(x: -bounds.minX, y: -bounds.minY)
    page.draw(with: .mediaBox, to: cg)
    guard let data = bitmap.representation(using: .png, properties: [:]) else { fatalError("PNG encoding failed") }
    try data.write(to: directory.appendingPathComponent(String(format: "page-%03d.png", index + 1)))
}
let data = try JSONSerialization.data(withJSONObject: ["source": args[0], "pages": document.pageCount, "page_records": records], options: [.prettyPrinted, .sortedKeys])
try data.write(to: directory.appendingPathComponent("text.json"))
print("Reviewed \(document.pageCount) PDF pages; rendered \(requested.count) pages in \(directory.path)")
