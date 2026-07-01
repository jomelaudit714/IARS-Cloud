"""IARS PDF textbox editor v2.9.

Fixes in this version:
- exact per-textbox font sizes from 6 to 48 pt without automatic shrinking
- font-size value remains visible when a textbox is deselected
- browser-local editing with no Streamlit rerun while typing, resizing, or selecting
- automatic idle synchronization to Streamlit with no manual save button
- one-click text editing after deselection
- long-press drag from text interior, immediate drag from plain borders, blue-handle resize
- no synchronization while a textbox or font-size field is actively being edited
- smoother return, delete, and retyping behavior in existing textboxes
- tighter text padding, Fit text, duplicate, resize, and page persistence
- component registration repeated safely on every Streamlit rerun
"""
from __future__ import annotations

from typing import Any

import streamlit as st


EDITOR_HTML = r"""
<div class="iars-pdf-editor">
  <div class="editor-toolbar">
    <div class="toolbar-group">
      <button type="button" id="zoom-out" title="Zoom out">−</button>
      <span id="zoom-label">100%</span>
      <button type="button" id="zoom-in" title="Zoom in">+</button>
      <button type="button" id="zoom-fit" title="Fit width">Fit width</button>
    </div>
    <div class="toolbar-group font-size-group">
      <label for="font-size-input">Font size</label>
      <input id="font-size-input" type="number" min="6" max="48" step="1" value="11" />
      <span class="font-unit">pt</span>
    </div>
    <div class="toolbar-group">
      <button type="button" id="fit-text" disabled>Fit text</button>
      <button type="button" id="duplicate-box" disabled>Duplicate</button>
      <button type="button" id="delete-box" class="danger" disabled>Delete</button>
      <button type="button" id="clear-page" class="danger-light">Clear page</button>
    </div>
    <div class="toolbar-group status-group">
      <span id="editor-status">Double-right-click the PDF to add a textbox.</span>
    </div>
  </div>
  <div class="editor-viewport" id="editor-viewport">
    <div class="page-stage" id="page-stage">
      <img id="page-image" alt="PDF page preview" draggable="false" />
      <div class="box-layer" id="box-layer"></div>
    </div>
  </div>
</div>
"""


EDITOR_CSS = r"""
:host {
  display: block;
  width: 100%;
  height: 100%;
  font-family: var(--st-font, Arial, sans-serif);
  color: var(--st-text-color, #1f2937);
}

.iars-pdf-editor {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  overflow: hidden;
  border: 1px solid color-mix(in srgb, var(--st-text-color, #111827) 20%, transparent);
  border-radius: 10px;
  background: var(--st-background-color, #ffffff);
}

.editor-toolbar {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding: 8px 10px;
  border-bottom: 1px solid color-mix(in srgb, var(--st-text-color, #111827) 18%, transparent);
  background: var(--st-secondary-background-color, #f3f4f6);
  z-index: 20;
}

.toolbar-group {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-group {
  min-width: 260px;
  flex: 1 1 320px;
}

#editor-status {
  font-size: 0.84rem;
  line-height: 1.25;
  color: color-mix(in srgb, var(--st-text-color, #111827) 72%, transparent);
}

button {
  appearance: none;
  border: 1px solid color-mix(in srgb, var(--st-text-color, #111827) 28%, transparent);
  border-radius: 6px;
  padding: 5px 10px;
  background: var(--st-background-color, #ffffff);
  color: var(--st-text-color, #111827);
  cursor: pointer;
  font: inherit;
  font-size: 0.84rem;
  font-weight: 600;
}

button:hover:not(:disabled) {
  border-color: var(--st-primary-color, #ff4b4b);
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

button.danger {
  color: #b91c1c;
  border-color: #fca5a5;
  background: #fef2f2;
}

button.danger-light {
  color: #991b1b;
}

button.save {
  color: #0f5132;
  border-color: #86d6a7;
  background: #ecfdf3;
}

button.save:not(:disabled) {
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.10);
}

#zoom-label {
  min-width: 45px;
  text-align: center;
  font-size: 0.84rem;
  font-variant-numeric: tabular-nums;
}

.font-size-group {
  padding: 3px 7px;
  border: 1px solid color-mix(in srgb, var(--st-text-color, #111827) 22%, transparent);
  border-radius: 7px;
  background: var(--st-background-color, #ffffff);
}

.font-size-group label {
  font-size: 0.82rem;
  font-weight: 700;
  white-space: nowrap;
}

#font-size-input {
  box-sizing: border-box;
  width: 58px;
  height: 29px;
  padding: 2px 5px;
  border: 1px solid color-mix(in srgb, var(--st-text-color, #111827) 28%, transparent);
  border-radius: 5px;
  background: var(--st-background-color, #ffffff);
  color: var(--st-text-color, #111827);
  font: inherit;
  font-size: 0.84rem;
  font-weight: 700;
  text-align: center;
}


.font-unit {
  font-size: 0.78rem;
  color: color-mix(in srgb, var(--st-text-color, #111827) 65%, transparent);
}

.editor-viewport {
  flex: 1 1 auto;
  min-height: 0;
  overflow: auto;
  padding: 18px;
  background: #d7dbe0;
  overscroll-behavior: contain;
}

.page-stage {
  position: relative;
  margin: 0 auto;
  width: 100%;
  max-width: none;
  background: #ffffff;
  box-shadow: 0 4px 18px rgba(0, 0, 0, 0.22);
  transform-origin: top center;
  user-select: none;
  touch-action: none;
}

#page-image {
  display: block;
  width: 100%;
  height: auto;
  pointer-events: none;
  user-select: none;
}

.box-layer {
  position: absolute;
  inset: 0;
  overflow: hidden;
  touch-action: none;
}

.tag-box {
  position: absolute;
  box-sizing: border-box;
  min-width: 34px;
  min-height: 16px;
  border: 1px solid #111827;
  background: rgba(255, 255, 255, 0.96);
  color: #111827;
  z-index: 3;
}

.tag-box.selected {
  outline: 2px dashed #2563eb;
  outline-offset: 2px;
  z-index: 5;
}

.tag-box.highlight {
  background: rgba(254, 249, 195, 0.96);
}

.tag-box.plain {
  border-color: transparent;
  background: transparent;
}

.drag-strip {
  position: absolute;
  left: -1px;
  top: -18px;
  width: 48px;
  height: 16px;
  box-sizing: border-box;
  border-radius: 4px 4px 0 0;
  cursor: move;
  background: #2563eb;
  color: #ffffff;
  display: none;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  line-height: 16px;
  z-index: 12;
  user-select: none;
}

.tag-box.selected .drag-strip {
  display: flex;
}

.drag-strip::after {
  content: "move";
}

.tag-text {
  position: absolute;
  inset: 0;
  box-sizing: border-box;
  padding: 1px 3px;
  overflow-x: auto;
  overflow-y: hidden;
  outline: none;
  white-space: nowrap;
  user-select: text;
  cursor: text;
  line-height: 1.05;
  scrollbar-width: none;
}

.tag-text::-webkit-scrollbar {
  display: none;
}

.tag-text:empty::before {
  content: "Type here";
  color: #6b7280;
  font-style: italic;
  pointer-events: none;
}

.drag-edge {
  position: absolute;
  z-index: 13;
  background: transparent;
  cursor: move;
  touch-action: none;
}

.drag-edge[data-side="top"] { left: 8px; right: 8px; top: -4px; height: 8px; }
.drag-edge[data-side="right"] { top: 8px; bottom: 8px; right: -4px; width: 8px; }
.drag-edge[data-side="bottom"] { left: 8px; right: 8px; bottom: -4px; height: 8px; }
.drag-edge[data-side="left"] { top: 8px; bottom: 8px; left: -4px; width: 8px; }

.tag-box.dragging,
.tag-box.dragging .tag-text {
  cursor: grabbing !important;
  user-select: none !important;
}

.resize-handle {
  position: absolute;
  width: 9px;
  height: 9px;
  box-sizing: border-box;
  border: 1px solid #ffffff;
  background: #2563eb;
  display: none;
  z-index: 14;
}

.tag-box.selected .resize-handle {
  display: block;
}

.resize-handle[data-dir="nw"] { left: -6px; top: -6px; cursor: nwse-resize; }
.resize-handle[data-dir="n"]  { left: calc(50% - 4px); top: -6px; cursor: ns-resize; }
.resize-handle[data-dir="ne"] { right: -6px; top: -6px; cursor: nesw-resize; }
.resize-handle[data-dir="e"]  { right: -6px; top: calc(50% - 4px); cursor: ew-resize; }
.resize-handle[data-dir="se"] { right: -6px; bottom: -6px; cursor: nwse-resize; }
.resize-handle[data-dir="s"]  { left: calc(50% - 4px); bottom: -6px; cursor: ns-resize; }
.resize-handle[data-dir="sw"] { left: -6px; bottom: -6px; cursor: nesw-resize; }
.resize-handle[data-dir="w"]  { left: -6px; top: calc(50% - 4px); cursor: ew-resize; }

.context-hint {
  position: fixed;
  z-index: 1000;
  padding: 5px 8px;
  border-radius: 5px;
  background: rgba(17, 24, 39, 0.94);
  color: white;
  font-size: 12px;
  pointer-events: none;
  transform: translate(8px, 8px);
}
"""


EDITOR_JS = r"""
export default function(component) {
  const { parentElement, data, setStateValue } = component;
  const root = parentElement.querySelector('.iars-pdf-editor');
  const viewport = parentElement.querySelector('#editor-viewport');
  const stage = parentElement.querySelector('#page-stage');
  const image = parentElement.querySelector('#page-image');
  const layer = parentElement.querySelector('#box-layer');
  const status = parentElement.querySelector('#editor-status');
  const zoomLabel = parentElement.querySelector('#zoom-label');
  const fontSizeInput = parentElement.querySelector('#font-size-input');
  const fitTextButton = parentElement.querySelector('#fit-text');
  const deleteButton = parentElement.querySelector('#delete-box');
  const duplicateButton = parentElement.querySelector('#duplicate-box');
  const clearButton = parentElement.querySelector('#clear-page');
  const zoomInButton = parentElement.querySelector('#zoom-in');
  const zoomOutButton = parentElement.querySelector('#zoom-out');
  const zoomFitButton = parentElement.querySelector('#zoom-fit');

  const pageNumber = Number(data?.page_number ?? 1);
  const pageKey = String(pageNumber);
  const storageKey = String(data?.storage_key ?? 'iars_pdf_editor_backup');
  const pythonEditor = data?.editor ?? {};

  function readLocalEditor() {
    try {
      const raw = window.localStorage.getItem(storageKey);
      return raw ? JSON.parse(raw) : null;
    } catch (_) {
      return null;
    }
  }

  const localEditor = readLocalEditor();
  const pythonUpdated = Number(pythonEditor?.updated_at ?? 0);
  const localUpdated = Number(localEditor?.updated_at ?? 0);
  let editor = localEditor && localUpdated > pythonUpdated ? localEditor : pythonEditor;

  let pages = editor?.pages && typeof editor.pages === 'object'
    ? structuredClone(editor.pages)
    : {};

  // Migration support for the v2.2 single-page state shape.
  if (Array.isArray(editor?.boxes) && !Array.isArray(pages[pageKey])) {
    pages[pageKey] = structuredClone(editor.boxes);
  }

  let boxes = Array.isArray(pages[pageKey]) ? structuredClone(pages[pageKey]) : [];
  let selectedId = Number(editor?.active_page ?? pageNumber) === pageNumber
    ? (editor?.selected_id ?? null)
    : null;
  let defaultFontSize = Number(editor?.default_font_size ?? 11);
  let zoom = Number(data?.zoom ?? 1);
  let operation = null;
  let textGesture = null;
  let suppressTextClickUntil = 0;
  const LONG_PRESS_MS = 360;
  const CLICK_MOVE_PX = 5;
  let lastRightClick = { time: 0, x: 0, y: 0 };
  let contextHint = null;
  let lastSnapshot = null;
  let localSaveTimer = null;
  let autoSyncTimer = null;
  let dirty = localUpdated > pythonUpdated;
  let syncing = false;
  const AUTOSAVE_IDLE_MS = 1800;
  let lastInteractionAt = performance.now();

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const clampFontSize = (value) => clamp(Number(value) || 11, 6, 48);
  defaultFontSize = clampFontSize(defaultFontSize);
  const makeId = () => `tag_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const currentBox = () => boxes.find((box) => box.id === selectedId) ?? null;

  function normalizeText(value) {
    return String(value ?? '').replace(/[\r\n]+/g, ' ').replace(/\s+/g, ' ').trim();
  }

  function normalizedBoxes() {
    return boxes.map((box) => {
      const exactFontSize = clampFontSize(box.font_size ?? box.base_font_size ?? 11);
      return {
        id: String(box.id),
        x_pct: Number(box.x_pct),
        y_pct: Number(box.y_pct),
        w_pct: Number(box.w_pct),
        h_pct: Number(box.h_pct),
        text: normalizeText(box.text),
        style: String(box.style ?? 'Box'),
        font_size: exactFontSize,
        base_font_size: exactFontSize,
      };
    });
  }

  function snapshot() {
    pages[pageKey] = normalizedBoxes();
    lastSnapshot = {
      pages: structuredClone(pages),
      selected_id: selectedId,
      active_page: pageNumber,
      default_font_size: defaultFontSize,
      updated_at: Date.now(),
    };
    return lastSnapshot;
  }

  function saveLocal() {
    const value = snapshot();
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(value));
    } catch (_) {
      // Browser storage may be disabled; Streamlit state remains the fallback.
    }
    return value;
  }

  function queueLocalSave(delay = 120) {
    if (localSaveTimer) window.clearTimeout(localSaveTimer);
    localSaveTimer = window.setTimeout(() => {
      localSaveTimer = null;
      saveLocal();
    }, delay);
  }

  function editorHasActiveInput() {
    const active = document.activeElement;
    return Boolean(
      operation ||
      layer.querySelector('.tag-text:focus') ||
      active === fontSizeInput
    );
  }

  function noteUserInteraction() {
    lastInteractionAt = performance.now();
    if (autoSyncTimer) {
      window.clearTimeout(autoSyncTimer);
      autoSyncTimer = null;
    }
  }

  function scheduleAutoSync(delay = AUTOSAVE_IDLE_MS) {
    if (autoSyncTimer) window.clearTimeout(autoSyncTimer);
    const elapsed = performance.now() - lastInteractionAt;
    const wait = Math.max(120, Number(delay) || AUTOSAVE_IDLE_MS, AUTOSAVE_IDLE_MS - elapsed);
    autoSyncTimer = window.setTimeout(() => {
      autoSyncTimer = null;
      if (!dirty || syncing) return;
      const idleFor = performance.now() - lastInteractionAt;
      if (editorHasActiveInput() || idleFor < AUTOSAVE_IDLE_MS) {
        scheduleAutoSync(Math.max(180, AUTOSAVE_IDLE_MS - idleFor));
        return;
      }
      syncToStreamlit();
    }, wait);
  }

  function markDirty(message = 'Saving changes automatically…', delay = AUTOSAVE_IDLE_MS) {
    dirty = true;
    noteUserInteraction();
    queueLocalSave(60);
    setStatus(message);
    scheduleAutoSync(Math.max(delay, AUTOSAVE_IDLE_MS));
  }

  function syncToStreamlit(message = 'All changes saved automatically.') {
    if (!dirty || syncing) return;
    if (localSaveTimer) {
      window.clearTimeout(localSaveTimer);
      localSaveTimer = null;
    }
    if (autoSyncTimer) {
      window.clearTimeout(autoSyncTimer);
      autoSyncTimer = null;
    }
    const value = saveLocal();
    syncing = true;
    dirty = false;
    setStatus('Saving…');
    setStateValue('editor', value);
    window.setTimeout(() => {
      syncing = false;
      setStatus(message);
    }, 220);
  }

  function setStatus(message) {
    status.textContent = message;
  }

  function setZoom(nextZoom) {
    zoom = clamp(nextZoom, 0.6, 2.5);
    stage.style.width = `${zoom * 100}%`;
    zoomLabel.textContent = `${Math.round(zoom * 100)}%`;
  }

  function fitWidth() {
    zoom = 1;
    stage.style.width = '100%';
    zoomLabel.textContent = 'Fit';
    viewport.scrollLeft = 0;
  }

  function refreshSelectionStyles() {
    layer.querySelectorAll('.tag-box').forEach((element) => {
      element.classList.toggle('selected', element.dataset.boxId === selectedId);
    });
    const selected = currentBox();
    const disabled = !selected;
    deleteButton.disabled = disabled;
    duplicateButton.disabled = disabled;
    fitTextButton.disabled = disabled;
    if (selected) {
      const selectedSize = clampFontSize(selected.font_size ?? selected.base_font_size ?? defaultFontSize);
      selected.font_size = selectedSize;
      selected.base_font_size = selectedSize;
      defaultFontSize = selectedSize;
      fontSizeInput.value = String(Math.round(selectedSize));
    } else {
      fontSizeInput.value = String(Math.round(defaultFontSize));
    }
  }

  function selectBox(id) {
    selectedId = id;
    refreshSelectionStyles();
  }

  function geometricCaretRange(textElement, clientX, clientY) {
    const walker = document.createTreeWalker(textElement, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    if (!nodes.length) {
      const emptyRange = document.createRange();
      emptyRange.selectNodeContents(textElement);
      emptyRange.collapse(true);
      return emptyRange;
    }

    let best = null;
    nodes.forEach((node) => {
      const length = node.textContent?.length ?? 0;
      for (let offset = 0; offset <= length; offset += 1) {
        const probe = document.createRange();
        let rect = null;
        let caretX = null;
        let centerY = null;
        if (length === 0) {
          probe.setStart(node, 0);
          probe.collapse(true);
          rect = probe.getBoundingClientRect();
          caretX = rect.left;
          centerY = rect.top + rect.height / 2;
        } else if (offset < length) {
          probe.setStart(node, offset);
          probe.setEnd(node, offset + 1);
          rect = probe.getBoundingClientRect();
          caretX = rect.left;
          centerY = rect.top + rect.height / 2;
        } else {
          probe.setStart(node, Math.max(0, length - 1));
          probe.setEnd(node, length);
          rect = probe.getBoundingClientRect();
          caretX = rect.right;
          centerY = rect.top + rect.height / 2;
        }
        if (!rect || (!rect.width && !rect.height)) continue;
        const distance = Math.abs(clientX - caretX) + Math.abs(clientY - centerY) * 3.2;
        if (!best || distance < best.distance) {
          const range = document.createRange();
          range.setStart(node, offset);
          range.collapse(true);
          best = { distance, range };
        }
      }
    });
    return best?.range ?? null;
  }

  function placeCaretAtPoint(textElement, clientX, clientY) {
    if (!textElement) return;
    let range = geometricCaretRange(textElement, clientX, clientY);

    if (!range && typeof document.caretPositionFromPoint === 'function') {
      const position = document.caretPositionFromPoint(clientX, clientY);
      if (position && textElement.contains(position.offsetNode)) {
        range = document.createRange();
        range.setStart(position.offsetNode, position.offset);
        range.collapse(true);
      }
    }
    if (!range && typeof document.caretRangeFromPoint === 'function') {
      const candidate = document.caretRangeFromPoint(clientX, clientY);
      if (candidate && textElement.contains(candidate.startContainer)) range = candidate;
    }
    if (!range) {
      range = document.createRange();
      range.selectNodeContents(textElement);
      range.collapse(false);
    }

    const applyRange = () => {
      const selection = window.getSelection?.();
      if (!selection || !textElement.isConnected) return;
      selection.removeAllRanges();
      selection.addRange(range.cloneRange());
    };
    textElement.focus({ preventScroll: true });
    applyRange();
    window.requestAnimationFrame(applyRange);
  }

  function clearTextGestureTimer() {
    if (textGesture?.timer) {
      window.clearTimeout(textGesture.timer);
      textGesture.timer = null;
    }
  }

  function beginLongPressTextDrag() {
    if (!textGesture || textGesture.dragging) return;
    const gesture = textGesture;
    const box = boxes.find((item) => item.id === gesture.id);
    if (!box) return;

    gesture.dragging = true;
    gesture.textElement.blur();
    window.getSelection?.()?.removeAllRanges();
    selectBox(gesture.id);
    const rect = stage.getBoundingClientRect();
    operation = {
      type: 'drag',
      id: gesture.id,
      pointerId: gesture.pointerId,
      startX: gesture.startX,
      startY: gesture.startY,
      startBox: structuredClone(box),
      stageWidth: rect.width,
      stageHeight: rect.height,
      moved: false,
      fromTextLongPress: true,
    };
    try {
      gesture.textElement.setPointerCapture(gesture.pointerId);
    } catch (_) {
      // Pointer capture is optional; window-level handlers remain active.
    }
    const boxElement = gesture.textElement.closest('.tag-box');
    boxElement?.classList.add('dragging');
    setStatus('Dragging textbox… release to save automatically.');
  }

  function handleTextPointerDown(event, id, textElement) {
    if (event.button !== 0) return;
    event.preventDefault();
    event.stopPropagation();
    noteUserInteraction();
    clearTextGestureTimer();
    selectBox(id);

    // Defer caret placement until pointer-up. Preventing the native pointer-down
    // default stops Chromium from overriding our exact character position.
    textGesture = {
      id,
      textElement,
      pointerId: event.pointerId,
      startX: event.clientX,
      startY: event.clientY,
      startTime: performance.now(),
      maxMovement: 0,
      dragging: false,
      timer: window.setTimeout(beginLongPressTextDrag, LONG_PRESS_MS),
    };
  }

  function handleTextPointerMove(event) {
    if (!textGesture || event.pointerId !== textGesture.pointerId) return;
    const distance = Math.hypot(
      event.clientX - textGesture.startX,
      event.clientY - textGesture.startY,
    );
    textGesture.maxMovement = Math.max(textGesture.maxMovement, distance);

    if (!textGesture.dragging && performance.now() - textGesture.startTime >= LONG_PRESS_MS) {
      beginLongPressTextDrag();
    }
    if (textGesture.dragging) {
      event.preventDefault();
    }
  }

  function endTextGesture(event, cancelled = false) {
    if (!textGesture || event.pointerId !== textGesture.pointerId) return;
    const gesture = textGesture;
    clearTextGestureTimer();
    textGesture = null;

    if (gesture.dragging) {
      event.preventDefault();
      event.stopPropagation();
      suppressTextClickUntil = performance.now() + 350;
      finishOperation();
      layer.querySelectorAll('.tag-box.dragging').forEach((element) => element.classList.remove('dragging'));
      return;
    }

    if (!cancelled && gesture.maxMovement <= CLICK_MOVE_PX) {
      event.preventDefault();
      event.stopPropagation();
      suppressTextClickUntil = performance.now() + 300;
      noteUserInteraction();
      selectBox(gesture.id);
      placeCaretAtPoint(gesture.textElement, gesture.startX, gesture.startY);
      setStatus('Editing… changes are saved automatically after 1.8 seconds of inactivity.');
    }
  }

  function handleTextPointerCancel(event) {
    endTextGesture(event, true);
  }

  function measureTextWidth(text, size) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) return Math.max(34, normalizeText(text).length * size * 0.58);
    ctx.font = `${size}px Arial, sans-serif`;
    return Math.max(1, ctx.measureText(normalizeText(text)).width);
  }

  function ensureBoxSupportsFont(box, { fitWidthToText = false } = {}) {
    if (!box) return;
    const rect = stage.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const size = clampFontSize(box.font_size ?? defaultFontSize);
    box.font_size = size;
    box.base_font_size = size;

    const requiredHeightPx = Math.max(18, size * 1.35 + 4);
    const requiredHeightPct = (requiredHeightPx / rect.height) * 100;
    if (box.h_pct < requiredHeightPct) {
      box.h_pct = Math.min(requiredHeightPct, 100 - box.y_pct);
    }

    if (fitWidthToText && normalizeText(box.text)) {
      const requiredWidthPx = measureTextWidth(box.text, size) + 10;
      const requiredWidthPct = (requiredWidthPx / rect.width) * 100;
      const desiredWidth = clamp(requiredWidthPct, 2.5, 88);
      if (desiredWidth > box.w_pct) {
        if (box.x_pct + desiredWidth <= 100) {
          box.w_pct = desiredWidth;
        } else {
          box.x_pct = Math.max(0, 100 - desiredWidth);
          box.w_pct = desiredWidth;
        }
      }
    }
  }

  function setSelectedFontSize(rawValue) {
    const parsed = Number(rawValue);
    if (String(rawValue).trim() === '' || !Number.isFinite(parsed)) return;
    const size = clampFontSize(parsed);
    defaultFontSize = size;
    fontSizeInput.value = String(Math.round(size));
    const box = currentBox();
    if (!box) {
      markDirty(`Default font size ${Math.round(size)} pt — saving automatically…`, 650);
      return;
    }
    box.font_size = size;
    box.base_font_size = size;
    ensureBoxSupportsFont(box, { fitWidthToText: true });
    const boxElement = layer.querySelector(`[data-box-id="${box.id}"]`);
    const textElement = boxElement?.querySelector('.tag-text');
    if (boxElement) {
      boxElement.style.left = `${box.x_pct}%`;
      boxElement.style.width = `${box.w_pct}%`;
      boxElement.style.height = `${box.h_pct}%`;
    }
    if (textElement) textElement.style.fontSize = `${size}px`;
    markDirty(`Font size ${Math.round(size)} pt — saving automatically…`, 650);
  }

  function showContextHint(clientX, clientY, message) {
    if (contextHint) contextHint.remove();
    contextHint = document.createElement('div');
    contextHint.className = 'context-hint';
    contextHint.textContent = message;
    contextHint.style.left = `${clientX}px`;
    contextHint.style.top = `${clientY}px`;
    document.body.appendChild(contextHint);
    window.setTimeout(() => {
      if (contextHint) {
        contextHint.remove();
        contextHint = null;
      }
    }, 800);
  }

  function fitSelectedToText() {
    const box = currentBox();
    if (!box) return;
    const stageRect = stage.getBoundingClientRect();
    if (!stageRect.width || !stageRect.height) return;

    const exactSize = clampFontSize(box.font_size ?? defaultFontSize);
    box.font_size = exactSize;
    box.base_font_size = exactSize;
    const desiredWidthPx = clamp(measureTextWidth(box.text, exactSize) + 10, 34, stageRect.width * 0.88);
    const desiredHeightPx = clamp(exactSize * 1.35 + 4, 18, 72);
    let desiredWidthPct = (desiredWidthPx / stageRect.width) * 100;
    let desiredHeightPct = (desiredHeightPx / stageRect.height) * 100;
    desiredWidthPct = Math.min(desiredWidthPct, 100);
    desiredHeightPct = Math.min(desiredHeightPct, 100);

    if (box.x_pct + desiredWidthPct > 100) box.x_pct = Math.max(0, 100 - desiredWidthPct);
    if (box.y_pct + desiredHeightPct > 100) box.y_pct = Math.max(0, 100 - desiredHeightPct);
    box.w_pct = desiredWidthPct;
    box.h_pct = desiredHeightPct;
    renderBoxes();
    markDirty('Textbox fitted — saving automatically…', 650);
  }

  function createBoxAt(clientX, clientY) {
    const rect = stage.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const xPct = clamp(((clientX - rect.left) / rect.width) * 100, 0, 96);
    const yPct = clamp(((clientY - rect.top) / rect.height) * 100, 0, 97);
    const defaultWidthPct = clamp((180 / rect.width) * 100, 15, 28);
    const defaultHeightPx = Math.max(24, defaultFontSize * 1.35 + 4);
    const defaultHeightPct = clamp((defaultHeightPx / rect.height) * 100, 1.6, 8);
    const box = {
      id: makeId(),
      x_pct: xPct,
      y_pct: yPct,
      w_pct: Math.min(defaultWidthPct, 99 - xPct),
      h_pct: Math.min(defaultHeightPct, 99 - yPct),
      text: '',
      style: 'Box',
      font_size: defaultFontSize,
      base_font_size: defaultFontSize,
    };
    boxes.push(box);
    selectedId = box.id;
    renderBoxes();
    markDirty('Textbox added — changes save automatically.', AUTOSAVE_IDLE_MS);
    window.setTimeout(() => {
      const text = layer.querySelector(`[data-box-id="${box.id}"] .tag-text`);
      if (text) text.focus({ preventScroll: true });
    }, 50);
  }

  function boxStyleClass(style) {
    if (style === 'Highlight Box') return ' highlight';
    if (style === 'Plain Text') return ' plain';
    return '';
  }

  function renderBoxes() {
    layer.replaceChildren();
    boxes.forEach((box) => {
      box.font_size = clampFontSize(box.font_size ?? box.base_font_size ?? defaultFontSize);
      box.base_font_size = box.font_size;
      ensureBoxSupportsFont(box);
      const boxElement = document.createElement('div');
      boxElement.className = `tag-box${box.id === selectedId ? ' selected' : ''}${boxStyleClass(box.style)}`;
      boxElement.dataset.boxId = box.id;
      boxElement.style.left = `${box.x_pct}%`;
      boxElement.style.top = `${box.y_pct}%`;
      boxElement.style.width = `${box.w_pct}%`;
      boxElement.style.height = `${box.h_pct}%`;

      const dragStrip = document.createElement('div');
      dragStrip.className = 'drag-strip';
      dragStrip.title = 'Drag to reposition';
      dragStrip.addEventListener('pointerdown', (event) => startDrag(event, box.id));

      const textElement = document.createElement('div');
      textElement.className = 'tag-text';
      textElement.contentEditable = 'true';
      textElement.spellcheck = false;
      textElement.tabIndex = 0;
      textElement.style.fontSize = `${box.font_size ?? 11}px`;
      textElement.innerText = normalizeText(box.text);
      textElement.addEventListener('pointerdown', (event) => {
        handleTextPointerDown(event, box.id, textElement);
      });
      textElement.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (performance.now() < suppressTextClickUntil) return;
        noteUserInteraction();
        selectBox(box.id);
        placeCaretAtPoint(textElement, event.clientX, event.clientY);
      });
      textElement.addEventListener('focus', () => selectBox(box.id));
      textElement.addEventListener('input', () => {
        // Keep typing entirely in the browser while the textbox is focused.
        // Automatic Streamlit synchronization waits until editing is idle.
        box.text = textElement.innerText;
        dirty = true;
        queueLocalSave(50);
        setStatus('Editing… changes are saved automatically when you pause.');
        noteUserInteraction();
        scheduleAutoSync(AUTOSAVE_IDLE_MS);
      });
      textElement.addEventListener('paste', (event) => {
        event.preventDefault();
        const pasted = normalizeText(event.clipboardData?.getData('text/plain') ?? '');
        document.execCommand('insertText', false, pasted);
      });
      textElement.addEventListener('blur', () => {
        box.text = normalizeText(textElement.innerText);
        textElement.innerText = box.text;
        markDirty('Text updated — saving automatically after a short pause…', AUTOSAVE_IDLE_MS);
      });
      textElement.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
          event.preventDefault();
          box.text = normalizeText(textElement.innerText);
          textElement.blur();
        }
        if (event.key === 'Escape') {
          textElement.blur();
        }
      });

      boxElement.addEventListener('pointerdown', (event) => {
        // The plain border/sides move the whole textbox. Blue handles remain
        // dedicated to resizing, and the text interior uses click-to-edit /
        // long-press-to-drag behavior.
        if (event.target === boxElement && event.button === 0) startDrag(event, box.id);
      });

      boxElement.appendChild(dragStrip);
      boxElement.appendChild(textElement);

      ['top', 'right', 'bottom', 'left'].forEach((side) => {
        const edge = document.createElement('div');
        edge.className = 'drag-edge';
        edge.dataset.side = side;
        edge.title = 'Drag to reposition';
        edge.addEventListener('pointerdown', (event) => startDrag(event, box.id));
        boxElement.appendChild(edge);
      });

      ['nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'].forEach((direction) => {
        const handle = document.createElement('div');
        handle.className = 'resize-handle';
        handle.dataset.dir = direction;
        handle.title = `Resize ${direction}`;
        handle.addEventListener('pointerdown', (event) => startResize(event, box.id, direction));
        boxElement.appendChild(handle);
      });

      layer.appendChild(boxElement);
    });
    refreshSelectionStyles();
  }

  function startDrag(event, id) {
    event.preventDefault();
    noteUserInteraction();
    event.stopPropagation();
    selectBox(id);
    const box = boxes.find((item) => item.id === id);
    const rect = stage.getBoundingClientRect();
    operation = {
      type: 'drag', id, pointerId: event.pointerId,
      startX: event.clientX, startY: event.clientY,
      startBox: structuredClone(box), stageWidth: rect.width, stageHeight: rect.height,
      moved: false,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function startResize(event, id, direction) {
    event.preventDefault();
    noteUserInteraction();
    event.stopPropagation();
    selectBox(id);
    const box = boxes.find((item) => item.id === id);
    const rect = stage.getBoundingClientRect();
    operation = {
      type: 'resize', id, direction, pointerId: event.pointerId,
      startX: event.clientX, startY: event.clientY,
      startBox: structuredClone(box), stageWidth: rect.width, stageHeight: rect.height,
      moved: false,
    };
    event.currentTarget.setPointerCapture(event.pointerId);
  }

  function updateOperation(event) {
    if (!operation) return;
    if (operation.fromTextLongPress) event.preventDefault();
    const box = boxes.find((item) => item.id === operation.id);
    if (!box) return;
    const dxPx = event.clientX - operation.startX;
    const dyPx = event.clientY - operation.startY;
    const dxPct = (dxPx / operation.stageWidth) * 100;
    const dyPct = (dyPx / operation.stageHeight) * 100;
    if (Math.hypot(dxPx, dyPx) > 1.5) operation.moved = true;
    const start = operation.startBox;

    if (operation.type === 'drag') {
      box.x_pct = clamp(start.x_pct + dxPct, 0, 100 - start.w_pct);
      box.y_pct = clamp(start.y_pct + dyPct, 0, 100 - start.h_pct);
    } else {
      const dir = operation.direction;
      let x = start.x_pct;
      let y = start.y_pct;
      let w = start.w_pct;
      let h = start.h_pct;
      const minW = Math.max(2.5, (34 / operation.stageWidth) * 100);
      const minHeightPx = Math.max(18, clampFontSize(box.font_size ?? defaultFontSize) * 1.35 + 4);
      const minH = Math.max(1.2, (minHeightPx / operation.stageHeight) * 100);

      if (dir.includes('e')) w = clamp(start.w_pct + dxPct, minW, 100 - start.x_pct);
      if (dir.includes('s')) h = clamp(start.h_pct + dyPct, minH, 100 - start.y_pct);
      if (dir.includes('w')) {
        x = clamp(start.x_pct + dxPct, 0, start.x_pct + start.w_pct - minW);
        w = start.w_pct + (start.x_pct - x);
      }
      if (dir.includes('n')) {
        y = clamp(start.y_pct + dyPct, 0, start.y_pct + start.h_pct - minH);
        h = start.h_pct + (start.y_pct - y);
      }
      box.x_pct = x;
      box.y_pct = y;
      box.w_pct = w;
      box.h_pct = h;
      ensureBoxSupportsFont(box);
    }

    const element = layer.querySelector(`[data-box-id="${box.id}"]`);
    if (element) {
      element.style.left = `${box.x_pct}%`;
      element.style.top = `${box.y_pct}%`;
      element.style.width = `${box.w_pct}%`;
      element.style.height = `${box.h_pct}%`;
      const textElement = element.querySelector('.tag-text');
      if (textElement) textElement.style.fontSize = `${box.font_size}px`;
    }
  }

  function finishOperation() {
    if (!operation) return;
    const finishedType = operation.type;
    const moved = Boolean(operation.moved);
    operation = null;
    layer.querySelectorAll('.tag-box.dragging').forEach((element) => element.classList.remove('dragging'));
    if (!moved) return;
    markDirty(finishedType === 'resize' ? 'Textbox resized — saving automatically…' : 'Textbox repositioned — saving automatically…', AUTOSAVE_IDLE_MS);
  }

  function deleteSelected() {
    if (!selectedId) return;
    boxes = boxes.filter((box) => box.id !== selectedId);
    selectedId = null;
    renderBoxes();
    markDirty('Textbox deleted — saving automatically…', AUTOSAVE_IDLE_MS);
  }

  function duplicateSelected() {
    const original = currentBox();
    if (!original) return;
    const duplicate = structuredClone(original);
    duplicate.id = makeId();
    duplicate.x_pct = clamp(original.x_pct + 2, 0, 100 - original.w_pct);
    duplicate.y_pct = clamp(original.y_pct + 2, 0, 100 - original.h_pct);
    boxes.push(duplicate);
    selectedId = duplicate.id;
    renderBoxes();
    markDirty('Textbox duplicated — saving automatically…', AUTOSAVE_IDLE_MS);
  }

  function clearPage() {
    if (boxes.length && !window.confirm('Remove all textboxes from this page?')) return;
    boxes = [];
    selectedId = null;
    renderBoxes();
    markDirty('Page cleared — saving automatically…', AUTOSAVE_IDLE_MS);
  }

  function flushFocusedText() {
    const focused = layer.querySelector('.tag-text:focus');
    if (!focused) return false;
    const boxElement = focused.closest('.tag-box');
    const box = boxes.find((item) => item.id === boxElement?.dataset?.boxId);
    if (!box) return false;
    box.text = normalizeText(focused.innerText);
    focused.innerText = box.text;
    dirty = true;
    saveLocal();
    setStatus('Text updated — saving automatically…');
    scheduleAutoSync(AUTOSAVE_IDLE_MS);
    return true;
  }

  function handleDocumentPointerDown(event) {
    const focused = layer.querySelector('.tag-text:focus');
    if (!focused) return;
    const path = event.composedPath?.() ?? [];
    if (!path.includes(focused)) flushFocusedText();
  }

  function handleContextMenu(event) {
    if (event.target.closest('.tag-box')) return;
    event.preventDefault();
    const now = performance.now();
    const distance = Math.hypot(event.clientX - lastRightClick.x, event.clientY - lastRightClick.y);
    if (now - lastRightClick.time <= 650 && distance <= 28) {
      lastRightClick = { time: 0, x: 0, y: 0 };
      createBoxAt(event.clientX, event.clientY);
    } else {
      lastRightClick = { time: now, x: event.clientX, y: event.clientY };
      showContextHint(event.clientX, event.clientY, 'Right-click again to add a textbox');
      setStatus('Right-click the same spot once more to add a textbox.');
    }
  }

  function handleKeydown(event) {
    const editing = event.composedPath().some(
      (node) => node?.classList?.contains?.('tag-text')
    );
    if (!editing && (event.key === 'Delete' || event.key === 'Backspace')) {
      event.preventDefault();
      deleteSelected();
    }
    if (!editing && event.key === 'Escape') selectBox(null);
  }

  layer.addEventListener('contextmenu', handleContextMenu);
  layer.addEventListener('pointerdown', (event) => {
    noteUserInteraction();
    if (event.target === layer) selectBox(null);
  });
  document.addEventListener('pointerdown', handleDocumentPointerDown, true);
  window.addEventListener('pointermove', handleTextPointerMove, { passive: false });
  window.addEventListener('pointermove', updateOperation, { passive: false });
  window.addEventListener('pointerup', endTextGesture);
  window.addEventListener('pointerup', finishOperation);
  window.addEventListener('pointercancel', handleTextPointerCancel);
  window.addEventListener('pointercancel', finishOperation);
  const handlePageHide = () => flushFocusedText();
  window.addEventListener('pagehide', handlePageHide);
  window.addEventListener('keydown', handleKeydown);
  fontSizeInput.addEventListener('input', () => setSelectedFontSize(fontSizeInput.value));
  fontSizeInput.addEventListener('change', () => setSelectedFontSize(fontSizeInput.value));
  fitTextButton.addEventListener('click', fitSelectedToText);
  deleteButton.addEventListener('click', deleteSelected);
  duplicateButton.addEventListener('click', duplicateSelected);
  clearButton.addEventListener('click', clearPage);
  zoomInButton.addEventListener('click', () => setZoom(zoom + 0.1));
  zoomOutButton.addEventListener('click', () => setZoom(zoom - 0.1));
  zoomFitButton.addEventListener('click', fitWidth);

  image.onload = () => {
    stage.style.aspectRatio = `${image.naturalWidth} / ${image.naturalHeight}`;
    setZoom(zoom);
    renderBoxes();
  };
  image.src = data?.image_data ?? '';
  renderBoxes();

  if (localEditor && localUpdated > pythonUpdated) {
    dirty = true;
    setStatus('Recovered local changes — saving automatically…');
    scheduleAutoSync(AUTOSAVE_IDLE_MS);
  } else {
    dirty = false;
    setStatus(pythonUpdated > 0
      ? 'All changes saved automatically.'
      : `Page ${pageNumber}. Changes save automatically.`);
  }

  return () => {
    flushFocusedText();
    layer.removeEventListener('contextmenu', handleContextMenu);
    document.removeEventListener('pointerdown', handleDocumentPointerDown, true);
    clearTextGestureTimer();
    window.removeEventListener('pointermove', handleTextPointerMove);
    window.removeEventListener('pointermove', updateOperation);
    window.removeEventListener('pointerup', endTextGesture);
    window.removeEventListener('pointerup', finishOperation);
    window.removeEventListener('pointercancel', handleTextPointerCancel);
    window.removeEventListener('pointercancel', finishOperation);
    if (localSaveTimer) window.clearTimeout(localSaveTimer);
    if (autoSyncTimer) window.clearTimeout(autoSyncTimer);
    window.removeEventListener('pagehide', handlePageHide);
    window.removeEventListener('keydown', handleKeydown);
    if (contextHint) contextHint.remove();
  };
}
"""


def _register_pdf_editor_component():
    """Register the Components v2 editor during every Streamlit script run.

    Streamlit rebuilds its component registry on each rerun, while imported Python
    modules remain cached. A module-level registration therefore exists only on
    the first run and causes "Component ... is not registered" after an upload
    or page change. Registering here keeps the component available on every run.
    """
    return st.components.v2.component(
        name="iars_pdf_textbox_editor_v29",
        html=EDITOR_HTML,
        css=EDITOR_CSS,
        js=EDITOR_JS,
        isolate_styles=True,
    )


def _read_editor_state(component_state: Any, default: dict[str, Any]) -> dict[str, Any]:
    if component_state is None:
        return default
    if isinstance(component_state, dict):
        value = component_state.get("editor", default)
    else:
        value = getattr(component_state, "editor", default)
    return value if isinstance(value, dict) else default


def pdf_textbox_editor(
    *,
    image_data: str,
    page_number: int,
    storage_key: str,
    key: str,
    height: int = 920,
):
    """Mount one persistent editor instance for all pages of one PDF."""
    initial_editor: dict[str, Any] = {
        "pages": {},
        "selected_id": None,
        "active_page": int(page_number),
        "default_font_size": 11,
        "updated_at": 0,
    }
    current_editor = _read_editor_state(st.session_state.get(key), initial_editor)

    component = _register_pdf_editor_component()

    return component(
        data={
            "image_data": image_data,
            "editor": current_editor,
            "page_number": int(page_number),
            "storage_key": storage_key,
            "zoom": 1.0,
        },
        default={"editor": current_editor},
        key=key,
        on_editor_change=lambda: None,
        width="stretch",
        height=height,
    )
