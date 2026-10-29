import recepten from '../data/recepten.json';
import boek from '../data/boek.json';
import eetclub from '../data/eetclub.json';

export { recepten, boek, eetclub };

export const hoofdstukken = boek.hoofdstukken;

export function hoofdstuk(slug) {
  return hoofdstukken.find((h) => h.slug === slug);
}

/** Alle pagina's van een hoofdstuk in boekvolgorde (recepten en eetclub-menu's). */
export function inhoud(slug) {
  const items = [
    ...recepten.filter((r) => r.hoofdstuk === slug).map((r) => ({ ...r, soort: 'recept' })),
    ...(slug === 'eetclub'
      ? eetclub.filter((e) => e.type === 'menu').map((e) => ({ ...e, hoofdstuk: 'eetclub', soort: 'menu' }))
      : []),
  ];
  return items.sort((a, b) => a.pagina - b.pagina);
}

/** Lineaire volgorde voor vorige/volgende-navigatie. */
export const volgorde = hoofdstukken.flatMap((h) => inhoud(h.slug));

export function url(item) {
  return `/${item.hoofdstuk}/${item.slug}/`;
}

export function foto(id, w = 960) {
  return `/fotos/${id}-${w}.webp`;
}

export function srcset(id) {
  return [480, 960, 1600].map((w) => `/fotos/${id}-${w}.webp ${w}w`).join(', ');
}

export function naam(item) {
  return item.ondertitel ? `${item.titel} ${item.ondertitel}` : item.titel;
}
