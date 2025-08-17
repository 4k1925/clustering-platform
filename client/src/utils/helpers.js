// src/utils/helpers.js
export function formatDate(date) {
  if (!date) return "";
  const d = new Date(date);
  // 简单实现（推荐使用 date-fns/dayjs 替代）
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
