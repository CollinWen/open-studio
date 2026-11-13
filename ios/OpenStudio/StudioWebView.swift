/**
 * StudioWebView: the website itself, in a web view, already signed in as the
 * owner. Before each page of the site starts, the owner token is put where
 * the site keeps a signed-in password (localStorage, the key in
 * frontend/src/api/ownerSignIn.ts), so the studio opens without asking.
 *
 * Pages on the site stay here; links to anywhere else (a source, YouTube)
 * open in Safari. Swipe back and forward, pull down to reload. File inputs
 * (the entry form's "add file") get the phone's own photo and camera picker.
 *
 * Used by StudioSiteView, which adds the words under it.
 */

import SwiftUI
import WebKit

struct StudioWebView: UIViewRepresentable {
    let site: URL
    let ownerToken: String
    /// Changed by StudioSiteView to send the page somewhere (studio, back).
    let command: WebCommand
    /// Told when a page can't load (nil once one does), so StudioSiteView can say so.
    let onProblem: (String?) -> Void

    /// Must match STORAGE_KEY in frontend/src/api/ownerSignIn.ts.
    private static let ownerTokenKey = "open-studio-owner-token"

    func makeCoordinator() -> Coordinator { Coordinator(site: site, onProblem: onProblem) }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.userContentController.addUserScript(signInScript())
        configuration.allowsInlineMediaPlayback = true

        let webView = WKWebView(frame: .zero, configuration: configuration)
        context.coordinator.webView = webView
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true
        webView.isOpaque = false
        webView.backgroundColor = .clear

        let refresh = UIRefreshControl()
        refresh.addTarget(context.coordinator, action: #selector(Coordinator.reload), for: .valueChanged)
        webView.scrollView.refreshControl = refresh

        webView.load(URLRequest(url: site.appending(path: "studio")))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        guard command.id != context.coordinator.lastCommandId else { return }
        context.coordinator.lastCommandId = command.id
        switch command.kind {
        case .none: break
        case .studio: webView.load(URLRequest(url: site.appending(path: "studio")))
        case .back: if webView.canGoBack { webView.goBack() }
        }
    }

    /// Writes the token before the site's own code runs, on the site's pages only.
    private func signInScript() -> WKUserScript {
        let origin = Self.origin(of: site)
        let source = """
        if (location.origin === \(Self.jsString(origin))) {
          try { localStorage.setItem(\(Self.jsString(Self.ownerTokenKey)), \(Self.jsString(ownerToken))); } catch (e) {}
        }
        """
        return WKUserScript(source: source, injectionTime: .atDocumentStart, forMainFrameOnly: true)
    }

    static func origin(of url: URL) -> String {
        var parts = URLComponents()
        parts.scheme = url.scheme
        parts.host = url.host()
        parts.port = url.port
        return parts.string ?? ""
    }

    /// A Swift string as a JavaScript string literal (JSON quoting is valid JavaScript).
    private static func jsString(_ text: String) -> String {
        let data = (try? JSONSerialization.data(withJSONObject: [text])) ?? Data("[\"\"]".utf8)
        return String(String(decoding: data, as: UTF8.self).dropFirst().dropLast())
    }

    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
        let siteOrigin: String
        let onProblem: (String?) -> Void
        weak var webView: WKWebView?
        var lastCommandId = 0

        init(site: URL, onProblem: @escaping (String?) -> Void) {
            siteOrigin = StudioWebView.origin(of: site)
            self.onProblem = onProblem
        }

        @objc func reload() {
            // Nothing loaded yet (the first load failed): start again from the studio.
            if webView?.url == nil, let start = URL(string: siteOrigin)?.appending(path: "studio") {
                webView?.load(URLRequest(url: start))
            } else {
                webView?.reload()
            }
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            webView.scrollView.refreshControl?.endRefreshing()
            onProblem(nil)
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            webView.scrollView.refreshControl?.endRefreshing()
            // A link sent to Safari cancels this load; that isn't a problem.
            let failure = error as NSError
            if failure.code == NSURLErrorCancelled || (failure.domain == "WebKitErrorDomain" && failure.code == 102) { return }
            onProblem("Couldn't reach the site. Pull down to try again.")
        }

        /// The site's own pages (and anything inside a page, like a YouTube player) stay; other links go to Safari.
        func webView(
            _ webView: WKWebView, decidePolicyFor action: WKNavigationAction,
            decisionHandler: @escaping (WKNavigationActionPolicy) -> Void
        ) {
            guard let url = action.request.url, action.targetFrame?.isMainFrame ?? true,
                  url.scheme == "http" || url.scheme == "https",
                  StudioWebView.origin(of: url) != siteOrigin
            else { return decisionHandler(.allow) }
            UIApplication.shared.open(url)
            decisionHandler(.cancel)
        }

        /// Links that ask for a new window (target="_blank") open in Safari, or here if they're the site's.
        func webView(
            _ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration,
            for action: WKNavigationAction, windowFeatures: WKWindowFeatures
        ) -> WKWebView? {
            if let url = action.request.url {
                if StudioWebView.origin(of: url) == siteOrigin { webView.load(action.request) } else { UIApplication.shared.open(url) }
            }
            return nil
        }
    }
}

/// A one-off instruction for the web view; a new id means "do it again".
struct WebCommand: Equatable {
    enum Kind { case none, studio, back }
    var kind: Kind = .none
    var id = 0

    mutating func send(_ kind: Kind) {
        self.kind = kind
        id += 1
    }
}
