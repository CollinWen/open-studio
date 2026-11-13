/**
 * MediaEditor: an entry's pictures and videos on its edit screen, one row
 * each: a small square of it, then cover (for the first) or its type, its
 * file size when known, and "make cover" and "remove". Under them, "add
 * photos or videos" opens the phone's picker; uploads show their progress.
 *
 * Used by EntryEditView; the work is in EntryEditModel.
 */

import SwiftUI

struct MediaEditor: View {
    @Bindable var model: EntryEditModel
    let api: StudioApi
    @State private var isPicking = false

    private static let squareSize: CGFloat = 3 * StudioStyle.line

    var body: some View {
        VStack(alignment: .leading, spacing: StudioStyle.line / 2) {
            ForEach(Array(model.media.enumerated()), id: \.offset) { index, item in
                HStack(alignment: .top, spacing: StudioStyle.wordGap) {
                    if let picture = api.pictureURL(of: item) {
                        CoverSquare(url: picture, size: Self.squareSize)
                    } else {
                        Text(item.type)
                            .font(StudioStyle.smallFont)
                            .foregroundStyle(StudioStyle.inkSoft)
                            .frame(width: Self.squareSize, height: Self.squareSize)
                            .background(StudioStyle.paperShade)
                    }
                    VStack(alignment: .leading, spacing: 2) {
                        Text(facts(of: item, at: index)).foregroundStyle(StudioStyle.inkSoft)
                        WordList {
                            if index > 0 {
                                Button("make cover") { withAnimation(StudioStyle.arrive) { model.makeCover(at: index) } }
                            }
                            Button("remove") { withAnimation(StudioStyle.leave) { model.removeMedia(at: index) } }
                                .foregroundStyle(StudioStyle.inkSoft)
                        }
                    }
                }
                .transition(.opacity)
            }
            if model.isUploading, let message = model.message {
                LoadingWord(text: message)
            } else {
                Button("add photos or videos") { isPicking = true }
                    .disabled(model.isSaving)
            }
        }
        .sheet(isPresented: $isPicking) {
            PhotoPicker { picked in
                isPicking = false
                Task { await model.addMedia(from: picked) }
            }
            .ignoresSafeArea()
        }
    }

    private func facts(of item: MediaItem, at index: Int) -> String {
        var parts = [index == 0 ? "cover" : item.type]
        if item.sizeBytes > 0 {
            parts.append(ByteCountFormatter.string(fromByteCount: Int64(item.sizeBytes), countStyle: .file))
        }
        return parts.joined(separator: " · ")
    }
}
