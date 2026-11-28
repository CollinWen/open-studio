/**
 * MarkdownText: text written in a TextEditor, shown as the studio's own
 * running text: paragraphs, headings, lists, quotes, code, rules, bold,
 * italic and links. A link to a path on this site opens in place; a web
 * address opens in a new tab.
 *
 * Draws React elements from markdownParser.ts, never HTML strings, so
 * nothing typed can run. Used by the entry page's notes, a board's brief
 * and the text editor's preview. Looks: .markdown in styles/base.css.
 */

import { Fragment, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { parseMarkdown, type Block, type Inline } from "./markdownParser";

interface Props {
  text: string;
  className?: string;
}

export function MarkdownText({ text, className }: Props) {
  return <div className={className ? `markdown ${className}` : "markdown"}>{parseMarkdown(text).map(drawBlock)}</div>;
}

function drawBlock(block: Block, key: number): ReactNode {
  switch (block.type) {
    case "paragraph":
      return <p key={key}>{drawInline(block.inline)}</p>;
    case "heading": {
      // The page's title is its h1, so the text's headings start one below it.
      const Heading = (["h2", "h3", "h4"] as const)[block.level - 1];
      return <Heading key={key}>{drawInline(block.inline)}</Heading>;
    }
    case "list": {
      const items = block.items.map((item, index) => <li key={index}>{item.map(drawBlock)}</li>);
      return block.ordered ? (
        <ol key={key} start={block.start}>
          {items}
        </ol>
      ) : (
        <ul key={key}>{items}</ul>
      );
    }
    case "quote":
      return <blockquote key={key}>{block.blocks.map(drawBlock)}</blockquote>;
    case "code":
      return (
        <pre key={key}>
          <code>{block.text}</code>
        </pre>
      );
    case "rule":
      return <hr key={key} />;
  }
}

function drawInline(pieces: Inline[]): ReactNode {
  return pieces.map((piece, key) => {
    switch (piece.type) {
      case "text":
        return <Fragment key={key}>{piece.text}</Fragment>;
      case "strong":
        return <strong key={key}>{drawInline(piece.children)}</strong>;
      case "em":
        return <em key={key}>{drawInline(piece.children)}</em>;
      case "code":
        return <code key={key}>{piece.text}</code>;
      case "break":
        return <br key={key} />;
      case "link":
        return piece.href.startsWith("/") ? (
          <Link key={key} to={piece.href} className="is-underlined">
            {drawInline(piece.children)}
          </Link>
        ) : (
          <a key={key} href={piece.href} className="is-underlined" target="_blank" rel="noopener noreferrer">
            {drawInline(piece.children)}
          </a>
        );
    }
  });
}
