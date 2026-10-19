const messages = {
  fr: {
    eyebrow: 'DONNÉES SYNTHÉTIQUES · VÉRITÉS DÉCLARÉES',
    title: 'Fabriquer les cas rares.\nConnaître leur réponse.',
    lede: 'Générez des cas sous contraintes avec des quotas exacts, puis modifiez le minimum de champs pour changer une étiquette. Chaque ligne est vérifiée sans demander à un modèle si elle est vraie.',
    generate: 'Composer le jeu',
    seed: 'Graine des objectifs aléatoires',
    run: 'Générer les cas →',
    truth:
      'Les règles définissent les étiquettes. Un avis Jev peut évaluer la plausibilité, mais ne remplace jamais ces règles.',
    download: 'Exporter le jeu JSON',
    cases: 'Des cas que l’on peut expliquer',
    synthetic: '100 % SYNTHÉTIQUE',
    count: 'cas générés',
    bad: 'cas avec écarts',
    exact: 'quotas demandés',
    case: 'Cas',
    received: 'Reçu',
    billed: 'Facturé',
    price: 'Prix accordé / facturé',
    total: 'Total · centimes',
    labels: 'Étiquettes',
    counterfactual: 'Le plus petit changement qui compte',
    choose:
      'Choisir un cas et une étiquette à inverser. Commande, réception et prix convenu restent figés ; les montants dérivés sont recalculés.',
    pair: 'Calculer la variante',
    limits:
      'Échantillonnage par objectifs aléatoires, sans garantie de distribution uniforme ou représentative. Les étiquettes ne sont vraies que relativement aux règles fournies. Les variantes sont des changements de données, pas des actions métier ou des preuves de causalité. Aucun modèle appelé depuis cette interface.',
    ready: 'sans écart déclaré',
    'quantity-only': 'écart de quantité',
    'price-only': 'écart de prix',
    combined: 'deux écarts',
    quantity_exceeds_receipt: 'quantité supérieure au reçu',
    price_mismatch: 'prix différent',
    yes: 'complets',
    partial: 'incomplets',
    busy: 'Résolution des contraintes…',
    done: 'Jeu généré et vérifié indépendamment.',
    error: 'Entrée non valide ou serveur indisponible.',
    optimal: 'MINIMUM DÉMONTRÉ',
    feasible: 'VARIANTE FAISABLE',
    infeasible: 'Aucune variante possible sous ces contraintes.',
    derived: 'Montant dérivé',
    nochange: 'Aucune intervention',
    intervention: 'Intervention',
    unchanged: 'faits figés conservés',
  },
  en: {
    eyebrow: 'SYNTHETIC DATA · DECLARED TRUTH',
    title: 'Create the rare cases.\nKnow their answers.',
    lede: 'Generate constrained cases with exact quotas, then change the fewest fields needed to flip a label. Each row is checked without asking a model whether it is true.',
    generate: 'Compose the dataset',
    seed: 'Random-target seed',
    run: 'Generate the cases →',
    truth:
      'Rules define labels. A Jev opinion can assess plausibility but never replaces these rules.',
    download: 'Export JSON dataset',
    cases: 'Cases we can explain',
    synthetic: '100% SYNTHETIC',
    count: 'generated cases',
    bad: 'cases with discrepancies',
    exact: 'requested quotas',
    case: 'Case',
    received: 'Received',
    billed: 'Billed',
    price: 'Agreed / billed price',
    total: 'Total · cents',
    labels: 'Labels',
    counterfactual: 'The smallest change that matters',
    choose:
      'Choose a case and a label to flip. Order, receipt and agreed price stay frozen; derived totals are recomputed.',
    pair: 'Compute the variant',
    limits:
      'Random-target optimization is not guaranteed uniform or representative sampling. Labels are true only relative to supplied rules. Variants change records; they are neither business actions nor causal evidence. This interface calls no model.',
    ready: 'no declared discrepancy',
    'quantity-only': 'quantity discrepancy',
    'price-only': 'price discrepancy',
    combined: 'both discrepancies',
    quantity_exceeds_receipt: 'quantity exceeds receipt',
    price_mismatch: 'price mismatch',
    yes: 'complete',
    partial: 'incomplete',
    busy: 'Solving constraints…',
    done: 'Dataset generated and independently checked.',
    error: 'Invalid input or server unavailable.',
    optimal: 'MINIMUM PROVEN',
    feasible: 'FEASIBLE VARIANT',
    infeasible: 'No possible variant under these constraints.',
    derived: 'Derived total',
    nochange: 'No intervention',
    intervention: 'Intervention',
    unchanged: 'frozen facts preserved',
  },
  es: {
    eyebrow: 'DATOS SINTÉTICOS · VERDADES DECLARADAS',
    title: 'Crear los casos raros.\nConocer sus respuestas.',
    lede: 'Genera casos bajo restricciones con cuotas exactas y cambia el mínimo de campos para invertir una etiqueta. Cada fila se verifica sin preguntar a un modelo si es verdadera.',
    generate: 'Componer el conjunto',
    seed: 'Semilla de objetivos aleatorios',
    run: 'Generar los casos →',
    truth:
      'Las reglas definen las etiquetas. Jev puede opinar sobre plausibilidad, pero nunca sustituye las reglas.',
    download: 'Exportar conjunto JSON',
    cases: 'Casos que podemos explicar',
    synthetic: '100 % SINTÉTICO',
    count: 'casos generados',
    bad: 'casos con diferencias',
    exact: 'cuotas solicitadas',
    case: 'Caso',
    received: 'Recibido',
    billed: 'Facturado',
    price: 'Precio acordado / facturado',
    total: 'Total · céntimos',
    labels: 'Etiquetas',
    counterfactual: 'El cambio mínimo que importa',
    choose:
      'Elegir un caso y una etiqueta que invertir. Pedido, recepción y precio acordado quedan fijos; se recalculan los totales derivados.',
    pair: 'Calcular variante',
    limits:
      'La optimización con objetivos aleatorios no garantiza muestreo uniforme ni representativo. Las etiquetas solo son verdaderas respecto a las reglas dadas. Las variantes modifican registros; no son acciones de negocio ni pruebas causales. Esta interfaz no llama a modelos.',
    ready: 'sin diferencia declarada',
    'quantity-only': 'diferencia de cantidad',
    'price-only': 'diferencia de precio',
    combined: 'ambas diferencias',
    quantity_exceeds_receipt: 'cantidad superior a la recibida',
    price_mismatch: 'precio distinto',
    yes: 'completas',
    partial: 'incompletas',
    busy: 'Resolviendo restricciones…',
    done: 'Conjunto generado y verificado independientemente.',
    error: 'Entrada no válida o servidor no disponible.',
    optimal: 'MÍNIMO DEMOSTRADO',
    feasible: 'VARIANTE FACTIBLE',
    infeasible: 'No hay variante posible bajo estas restricciones.',
    derived: 'Total derivado',
    nochange: 'Sin intervención',
    intervention: 'Intervención',
    unchanged: 'hechos fijos conservados',
  },
};
const lang = new URLSearchParams(location.search).get('lang') || 'en',
  m = messages[lang] || messages.en;
document.documentElement.lang = messages[lang] ? lang : 'en';
document.querySelectorAll('[data-i18n]').forEach((x) => (x.textContent = m[x.dataset.i18n]));
document.querySelectorAll('nav a').forEach((a) => {
  if (a.textContent.toLowerCase() === document.documentElement.lang)
    a.setAttribute('aria-current', 'page');
});
const $ = (id) => document.getElementById(id),
  el = (tag, text, cls) => {
    const x = document.createElement(tag);
    if (text !== undefined) x.textContent = text;
    if (cls) x.className = cls;
    return x;
  };
for (const option of $('label-select').options) option.textContent = m[option.value];
let spec, dataset;
function render(data) {
  dataset = data;
  $('count').textContent = data.records.length;
  $('bad').textContent = data.records.filter((r) => !r.labels.ready).length;
  $('exact').textContent = data.status === 'complete' ? m.yes : m.partial;
  $('rows').replaceChildren();
  $('case-select').replaceChildren();
  for (const r of data.records) {
    const v = r.values,
      tr = el('tr');
    tr.append(
      el('td', r.id),
      el('td', v.received_quantity),
      el('td', v.billed_quantity),
      el('td', `${v.agreed_unit_cents} / ${v.billed_unit_cents}`),
      el('td', v.invoice_total_cents),
      el('td', m[r.cohort]),
    );
    if (!r.labels.ready) tr.className = 'discrepancy';
    $('rows').append(tr);
    const option = el('option', r.id + ' · ' + m[r.cohort]);
    option.value = r.id;
    $('case-select').append(option);
  }
  const selected = data.records.find((r) => r.cohort === 'quantity-only');
  if (selected) $('case-select').value = selected.id;
  $('pair-result').replaceChildren();
  $('digest').textContent = data.spec_sha256;
  $('status').textContent = data.status === 'complete' ? m.done : m.partial;
}
async function generate() {
  $('generate').disabled = true;
  $('status').textContent = m.busy;
  try {
    for (const input of document.querySelectorAll('[data-cohort]'))
      spec.cohorts.find((c) => c.id === input.dataset.cohort).count = Number(input.value);
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ spec, seed: Number($('seed').value) }),
    });
    if (!response.ok) throw Error();
    render(await response.json());
  } catch {
    $('status').textContent = m.error;
  } finally {
    $('generate').disabled = false;
  }
}
async function pair() {
  $('pair').disabled = true;
  try {
    const row = dataset.records.find((r) => r.id === $('case-select').value);
    const response = await fetch('/api/pair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        spec: dataset.source_spec,
        row: row.values,
        label: $('label-select').value,
      }),
    });
    if (!response.ok) throw Error();
    const result = await response.json();
    $('pair-result').replaceChildren();
    $('pair-result').append(
      el(
        'strong',
        result.status === 'OPTIMAL' ? m.optimal : result.row ? m.feasible : m.infeasible,
        'pair-verdict',
      ),
    );
    if (result.row) {
      for (const [k, v] of Object.entries(result.interventions)) {
        const change = el('div', undefined, 'change');
        change.append(el('span', k), el('span', `${v.before} → ${v.after}`));
        $('pair-result').append(change);
      }
      for (const [k, v] of Object.entries(result.derived_changes)) {
        const change = el('div', undefined, 'change derived');
        change.append(el('span', m.derived + ' · ' + k), el('span', `${v.before} → ${v.after}`));
        $('pair-result').append(change);
      }
      $('pair-result').append(el('p', m.unchanged, 'hint'));
    }
  } catch {
    $('status').textContent = m.error;
  } finally {
    $('pair').disabled = false;
  }
}
$('generate').addEventListener('click', generate);
$('pair').addEventListener('click', pair);
$('download').addEventListener('click', () => {
  if (!dataset) return;
  const url = URL.createObjectURL(
      new Blob([JSON.stringify(dataset, null, 2)], { type: 'application/json' }),
    ),
    a = el('a');
  a.href = url;
  a.download = 'synthcase-dataset.json';
  a.click();
  URL.revokeObjectURL(url);
});
try {
  const response = await fetch('/api/example');
  if (!response.ok) throw Error();
  spec = await response.json();
  for (const c of spec.cohorts) {
    const label = el('label', undefined, 'quota');
    label.append(el('span', m[c.id]));
    const input = el('input');
    input.type = 'number';
    input.min = 0;
    input.max = 20;
    input.value = c.count;
    input.dataset.cohort = c.id;
    label.append(input);
    $('quotas').append(label);
  }
  await generate();
} catch {
  $('status').textContent = m.error;
}
