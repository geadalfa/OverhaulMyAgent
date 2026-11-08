import Foundation
import Vision
import AppKit

struct OCRResult: Codable {
    let text: String
    let confidence: Float
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

func upscaleIfNeeded(cgImage: CGImage) -> CGImage {
    let w = cgImage.width
    let h = cgImage.height
    // Upscale low-res/small text (height < 500) to ensure high OCR precision
    let scale: CGFloat = (h < 500) ? (h < 250 ? 3.0 : 2.0) : 1.0
    
    if scale == 1.0 { return cgImage }
    
    let targetW = Int(CGFloat(w) * scale)
    let targetH = Int(CGFloat(h) * scale)
    let colorSpace = CGColorSpaceCreateDeviceRGB()
    
    guard let ctx = CGContext(
        data: nil,
        width: targetW,
        height: targetH,
        bitsPerComponent: 8,
        bytesPerRow: 0,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { return cgImage }
    
    ctx.interpolationQuality = .high
    ctx.draw(cgImage, in: CGRect(x: 0, y: 0, width: targetW, height: targetH))
    return ctx.makeImage() ?? cgImage
}

func processImage(path: String, asJson: Bool) {
    let expandedPath = NSString(string: path).expandingTildeInPath
    guard FileManager.default.fileExists(atPath: expandedPath) else {
        fputs("Error: File does not exist at path: \(path)\n", stderr)
        return
    }
    
    guard let nsImage = NSImage(contentsOfFile: expandedPath) else {
        fputs("Error: Cannot read image at path: \(path)\n", stderr)
        return
    }
    
    var rect = NSRect(origin: .zero, size: nsImage.size)
    guard let baseCG = nsImage.cgImage(forProposedRect: &rect, context: nil, hints: nil) else {
        fputs("Error: Could not extract CGImage from: \(path)\n", stderr)
        return
    }
    
    let cgImage = upscaleIfNeeded(cgImage: baseCG)
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false
    
    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    do {
        try handler.perform([request])
        guard let results = request.results else { return }
        
        // Sort top to bottom (descending y), then left to right (ascending x)
        let sorted = results.sorted { a, b in
            let yDiff = abs(a.boundingBox.origin.y - b.boundingBox.origin.y)
            if yDiff > 0.02 {
                return a.boundingBox.origin.y > b.boundingBox.origin.y
            }
            return a.boundingBox.origin.x < b.boundingBox.origin.x
        }
        
        if asJson {
            let output = sorted.compactMap { obs -> OCRResult? in
                guard let candidate = obs.topCandidates(1).first else { return nil }
                let bb = obs.boundingBox
                return OCRResult(
                    text: candidate.string,
                    confidence: candidate.confidence,
                    x: Double(bb.origin.x),
                    y: Double(bb.origin.y),
                    width: Double(bb.size.width),
                    height: Double(bb.size.height)
                )
            }
            let encoder = JSONEncoder()
            encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
            if let data = try? encoder.encode(output), let str = String(data: data, encoding: .utf8) {
                print(str)
            }
        } else {
            for obs in sorted {
                if let top = obs.topCandidates(1).first {
                    print(top.string)
                }
            }
        }
    } catch {
        fputs("Vision OCR Error on \(path): \(error)\n", stderr)
    }
}

let args = CommandLine.arguments
var asJson = false
var imagePaths: [String] = []

for arg in args.dropFirst() {
    if arg == "--json" || arg == "-j" {
        asJson = true
    } else if arg == "--help" || arg == "-h" {
        print("Usage: ocr [--json] <image-path-1> [image-path-2 ...]")
        print("Fast native Apple Silicon Vision OCR tool (< 500ms).")
        exit(0)
    } else {
        imagePaths.append(arg)
    }
}

if imagePaths.isEmpty {
    fputs("Usage: ocr [--json] <image-path>\n", stderr)
    exit(1)
}

for path in imagePaths {
    processImage(path: path, asJson: asJson)
}
