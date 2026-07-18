const SHADOW_PRESETS = {
  theme: null,
  none: 'none',
  subtle: '0 2px 8px rgba(0, 0, 0, 0.14)',
  medium: '0 6px 18px rgba(0, 0, 0, 0.2)',
  strong: '0 12px 32px rgba(0, 0, 0, 0.28)'
};

const SHADOW_GEOMETRY = {
  subtle: '0 2px 8px',
  medium: '0 6px 18px',
  strong: '0 12px 32px'
};

function setSupportedStyle(element, property, value) {
  if (typeof value !== 'string' || !value.trim()) return;
  if (globalThis.CSS?.supports?.(property, value)) {
    element.style.setProperty(property, value);
  }
}

export function applyCardAppearance(root, config) {
  const card = root?.querySelector('.card');
  if (!card) return;

  const appearance = config?.appearance || {};
  const coloredPreset = appearance.shadow_color && SHADOW_GEOMETRY[appearance.shadow]
    ? `${SHADOW_GEOMETRY[appearance.shadow]} ${appearance.shadow_color}`
    : null;
  const shadow = appearance.custom_shadow || coloredPreset || SHADOW_PRESETS[appearance.shadow];

  [
    'box-shadow', 'background-color', 'border-color', 'border-width',
    'border-style', 'border-radius', 'color', 'font-family', 'padding',
    'backdrop-filter', '-webkit-backdrop-filter', '--ookla-accent-color'
  ].forEach(property => card.style.removeProperty(property));

  if (shadow) setSupportedStyle(card, 'box-shadow', shadow);
  if (appearance.shadow === 'none') card.style.setProperty('box-shadow', 'none');

  setSupportedStyle(card, 'background-color', appearance.background_color);
  setSupportedStyle(card, 'border-color', appearance.border_color);
  setSupportedStyle(card, 'color', appearance.text_color);
  setSupportedStyle(card, 'font-family', appearance.font_family);
  setSupportedStyle(card, '--ookla-accent-color', appearance.accent_color);

  const pixelOptions = {
    border_width: ['border-width', 0, 10],
    border_radius: ['border-radius', 0, 64],
    backdrop_blur: ['backdrop-filter', 0, 60],
    padding: ['padding', 0, 64]
  };

  Object.entries(pixelOptions).forEach(([key, [property, min, max]]) => {
    if (appearance[key] === undefined || appearance[key] === '') return;
    const value = Math.min(Math.max(Number(appearance[key]), min), max);
    if (!Number.isFinite(value)) return;
    const cssValue = key === 'backdrop_blur' ? `blur(${value}px)` : `${value}px`;
    card.style.setProperty(property, cssValue);
    if (key === 'border_width' && value > 0) card.style.setProperty('border-style', 'solid');
    if (key === 'backdrop_blur') card.style.setProperty('-webkit-backdrop-filter', cssValue);
  });
}

export function createAppearanceEditor(editor) {
  const appearance = editor._config.appearance || {};
  const section = document.createElement('div');
  section.style.cssText = 'border: 1px solid var(--divider-color); border-radius: 8px; padding: 12px; background: var(--card-background-color);';

  const heading = document.createElement('div');
  heading.textContent = 'Card Appearance';
  heading.style.cssText = 'font-size: 13px; font-weight: 600; color: var(--primary-text-color); margin-bottom: 12px;';
  section.appendChild(heading);

  const update = (key, value) => {
    const nextAppearance = { ...(editor._config.appearance || {}) };
    if (value === '' || value === undefined) delete nextAppearance[key];
    else nextAppearance[key] = value;
    editor.configChanged({ ...editor._config, appearance: nextAppearance });
  };

  const addRow = (labelText, control) => {
    const row = document.createElement('label');
    row.style.cssText = 'display: grid; grid-template-columns: minmax(120px, 1fr) minmax(120px, 1fr); align-items: center; gap: 12px; margin-bottom: 10px; color: var(--secondary-text-color); font-size: 12px;';
    const label = document.createElement('span');
    label.textContent = labelText;
    row.append(label, control);
    section.appendChild(row);
  };

  const inputStyle = 'width: 100%; min-width: 0; box-sizing: border-box; padding: 7px 8px; border: 1px solid var(--divider-color); border-radius: 4px; background: var(--secondary-background-color); color: var(--primary-text-color);';

  const shadow = document.createElement('select');
  shadow.style.cssText = inputStyle;
  ['theme', 'none', 'subtle', 'medium', 'strong'].forEach(value => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = value[0].toUpperCase() + value.slice(1);
    option.selected = value === (appearance.shadow || 'theme');
    shadow.appendChild(option);
  });
  shadow.addEventListener('change', event => update('shadow', event.target.value));
  addRow('Shadow', shadow);

  const textFields = [
    ['custom_shadow', 'Custom shadow', 'e.g. 0 8px 24px rgba(0,0,0,.2)'],
    ['font_family', 'Font family', 'Theme default']
  ];
  textFields.forEach(([key, label, placeholder]) => {
    const input = document.createElement('input');
    input.type = 'text';
    input.value = appearance[key] || '';
    input.placeholder = placeholder;
    input.style.cssText = inputStyle;
    input.addEventListener('change', event => update(key, event.target.value.trim()));
    addRow(label, input);
  });

  const colorFields = [
    ['shadow_color', 'Shadow color', '#000000'],
    ['background_color', 'Background color', '#1f2937'],
    ['border_color', 'Border color', '#64748b'],
    ['text_color', 'Text color', '#f8fafc'],
    ['accent_color', 'Accent color', '#0ea5e9']
  ];
  colorFields.forEach(([key, label, fallback]) => {
    const control = document.createElement('div');
    control.style.cssText = 'display: grid; grid-template-columns: 42px minmax(0, 1fr); gap: 6px; min-width: 0;';

    const picker = document.createElement('input');
    picker.type = 'color';
    picker.value = /^#[0-9a-f]{6}$/i.test(appearance[key] || '') ? appearance[key] : fallback;
    picker.title = `Choose ${label.toLowerCase()}`;
    picker.style.cssText = 'width: 42px; height: 34px; box-sizing: border-box; padding: 2px; border: 1px solid var(--divider-color); border-radius: 4px; background: var(--secondary-background-color); cursor: pointer;';

    const text = document.createElement('input');
    text.type = 'text';
    text.value = appearance[key] || '';
    text.placeholder = 'Theme default';
    text.style.cssText = inputStyle;

    picker.addEventListener('input', event => {
      text.value = event.target.value;
      update(key, event.target.value);
    });
    text.addEventListener('change', event => {
      const value = event.target.value.trim();
      if (/^#[0-9a-f]{6}$/i.test(value)) picker.value = value;
      update(key, value);
    });

    control.append(picker, text);
    addRow(label, control);
  });

  const numberFields = [
    ['border_width', 'Border width', 0, 10, 1],
    ['border_radius', 'Corner radius', 0, 64, 1],
    ['backdrop_blur', 'Backdrop blur', 0, 60, 1],
    ['padding', 'Card padding', 0, 64, 1]
  ];
  numberFields.forEach(([key, label, min, max, step]) => {
    const input = document.createElement('input');
    input.type = 'number';
    input.value = appearance[key] ?? '';
    input.placeholder = 'Theme default';
    input.min = String(min);
    input.max = String(max);
    input.step = String(step);
    input.style.cssText = inputStyle;
    input.addEventListener('change', event => update(key, event.target.value === '' ? '' : Number(event.target.value)));
    addRow(`${label} (px)`, input);
  });

  return section;
}
