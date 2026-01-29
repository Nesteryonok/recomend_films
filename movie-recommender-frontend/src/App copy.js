// src/App.js
import React, { useState } from 'react';

function App() {
  const [ratingsFile, setRatingsFile] = useState(null);
  const [productsFile, setProductsFile] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Улучшенный парсер CSV с поддержкой кавычек
  const parseCSV = (text) => {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());

    return lines.slice(1).map(line => {
      const values = [];
      let current = '';
      let inQuotes = false;

      for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
          inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
          values.push(current.trim());
          current = '';
        } else {
          current += char;
        }
      }
      values.push(current.trim());

      const obj = {};
      headers.forEach((h, i) => {
        const val = values[i] || '';
        obj[h] = isNaN(val) ? val : Number(val);
      });
      return obj;
    });
  };

  const handleRecommend = async () => {
    if (!ratingsFile || !productsFile) return;

    setLoading(true);

    try {
      const ratingsText = await ratingsFile.text();
      const productsText = await productsFile.text();

      const ratings = parseCSV(ratingsText);
      const products = parseCSV(productsText);

      // Создаём маппинг product_id → title
      const productMap = {};
      products.forEach(p => {
        productMap[p.product_id] = p.title;
      });

      // Агрегируем рейтинги по productId
      const ratingSums = {};
      const ratingCounts = {};

      ratings.forEach(r => {
        const id = r.productId;
        ratingSums[id] = (ratingSums[id] || 0) + r.rating;
        ratingCounts[id] = (ratingCounts[id] || 0) + 1;
      });

      // Считаем средние
      const avgRatings = Object.keys(ratingSums).map(id => {
        const avg = ratingSums[id] / ratingCounts[id];
        return {
          id: Number(id),
          avg,
          title: productMap[id] || `Unknown (ID ${id})`
        };
      });

      // Сортируем по среднему (убывание) и берём топ-10
      avgRatings.sort((a, b) => b.avg - a.avg);
      const top10 = avgRatings.slice(0, 10);

      setTopProducts(top10);
    } catch (err) {
      console.error('Ошибка обработки:', err);
      alert('Не удалось обработать файлы. Проверьте формат CSV.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '700px', margin: '0 auto', fontFamily: 'Arial' }}>
      <h2>🎬 Рекомендательная система (без сервера)</h2>
      <p>Загрузите два CSV-файла:</p>

      <div style={{ marginBottom: '15px' }}>
        <label>Файл с рейтингами (ratings.csv):</label>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setRatingsFile(e.target.files[0])}
          style={{ display: 'block', marginTop: '5px' }}
        />
      </div>

      <div style={{ marginBottom: '15px' }}>
        <label>Файл с продуктами (products1.csv):</label>
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setProductsFile(e.target.files[0])}
          style={{ display: 'block', marginTop: '5px' }}
        />
      </div>

      <button
        onClick={handleRecommend}
        disabled={!ratingsFile || !productsFile || loading}
        style={{
          padding: '8px 16px',
          backgroundColor: '#4CAF50',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        {loading ? 'Обработка...' : 'Получить рекомендации'}
      </button>

      {topProducts.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h3>🔥 Топ-10 рекомендуемых продуктов:</h3>
          <ol>
            {topProducts.map((item, i) => (
              <li key={i} style={{ margin: '10px 0' }}>
                <strong>{item.title}</strong> — средний рейтинг: {item.avg.toFixed(2)}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export default App;