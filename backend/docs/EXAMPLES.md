# API Examples & Use Cases

## Example Requests & Responses

### 1. Simple Breakfast Recommendation

**Request:**
```json
{
  "message": "Rekomendasi tempat sarapan yang enak dong",
  "conversation_history": []
}
```

**Response:**
```json
{
  "message": "Selamat pagi! Saat ini jam 08:30 WITA, waktu yang pas untuk sarapan. Berikut rekomendasi tempat sarapan yang enak dan sedang buka:\n\n1. **Sarapan Simpang Kartini** (Buka Sekarang)\n   - Menyajikan sarapan khas Banjar yang autentik\n   - Menu andalan: Soto Banjar, Rawon, Lupis, Buras\n   - Harga sangat terjangkau mulai dari 5 ribuan\n   - Lokasi: Dewi Sartika, Samarinda\n   - Cocok untuk yang suka masakan tradisional Banjar\n\n2. **Laras Japanese Food** (Buka dalam 2 jam)\n   - Sarapan ala Jepang dengan porsi jumbo\n   - Menu: Chicken Wafuyaki, Chicken Katsu\n   - Harga murah di bawah 20 ribu\n   - Lokasi: Cilandak, Jakarta\n\nSaya rekomendasikan Sarapan Simpang Kartini karena sedang buka dan sangat cocok untuk sarapan pagi dengan menu tradisional yang mengenyangkan!",
  "restaurants": [
    {
      "nama_tempat": "Sarapan Simpang Kartini",
      "ringkasan": "Sarapan Simpang Kartini di Samarinda menawarkan pengalaman sarapan ala Banjar yang autentik dengan suasana yang lebih rapi.",
      "kategori_makanan": "Sarapan Banjar",
      "range_harga": "Murah (<20k)",
      "link_lokasi": "https://maps.google.com/...",
      "link_instagram": "https://www.instagram.com/p/DNhVte6Ppb2/",
      "jam_buka": "07:00",
      "jam_tutup": "12:00",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Lupis", "Buras", "Soto Banjar", "Rawon", "Nasi Kebuli"],
      "fasilitas": []
    }
  ]
}
```

### 2. Budget-Conscious Lunch

**Request:**
```json
{
  "message": "Cari tempat makan siang yang murah, budget dibawah 20 ribu",
  "conversation_history": []
}
```

**Response:**
```json
{
  "message": "Siang ini jam 12:45 WITA, pas banget untuk makan siang! Berikut rekomendasi tempat makan dengan budget di bawah 20 ribu yang sedang buka:\n\n1. **Kedai Uncle Tao** (Buka Sekarang)\n   - Kedai murah meriah dekat kampus Unmul\n   - Menu andalan: Sambal Matah, Pisang Wijen, Ayam Suwir\n   - Harga mulai 8 ribu saja!\n   - Ada WiFi dan suasana cozy untuk nongkrong\n   - Lokasi: Jl. Ery Suparjan, Perumahan TVRI Samarinda\n\n2. **Ayam Sambal Pecok** (Buka Sekarang)\n   - Spesialis ayam dengan sambal pecak yang gurih pedas\n   - Harga terjangkau sekitar 18 ribu\n   - Menu: Ayam, Ikan Nila, Bebek dengan sambal pecak\n   - Lokasi: Lokalaya Samarinda\n\nKedua tempat ini sangat recommended untuk budget kamu dan sedang buka sekarang!",
  "restaurants": [
    {
      "nama_tempat": "kedai @kedaiuncletao",
      "ringkasan": "Kedai @kedaiuncletao adalah tempat makan murah meriah di sekitar Unmul yang menawarkan menu lezat dengan harga terjangkau.",
      "kategori_makanan": "Ayam & Sambal",
      "range_harga": "Murah (<20k)",
      "link_lokasi": "https://maps.google.com/...",
      "link_instagram": "https://www.instagram.com/p/DNrq0sSZP9F/",
      "jam_buka": "10:00",
      "jam_tutup": "22:00",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Sambal Matah", "Pisang Wijen", "Ayam Suwir"],
      "fasilitas": ["wifi", "cozy"]
    }
  ]
}
```

### 3. Evening Hangout with View

**Request:**
```json
{
  "message": "Mau nongkrong sore sambil liat pemandangan bagus, ada rekomendasi?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "message": "Wah, sore ini jam 17:30 WITA, waktu yang sempurna untuk nongkrong sambil menikmati sunset! Saya punya rekomendasi tempat dengan view keren:\n\n1. **F3 Coffe & City View** (Buka Sekarang)\n   - Pemandangan kota Samarinda dari atas yang spektakuler!\n   - Semakin senja semakin indah viewnya\n   - Menu: Ayam Saus Mentega, Bulgogi, Kopi Pandan, Red Velvet Boba\n   - Harga variatif, ada yang terjangkau\n   - Fasilitas: City view, outdoor seating, musholla\n   - Lokasi: Jl. Teuku Umar, Samarinda\n   - Jam operasional: 10:00 - 23:00\n\n2. **McDonald's (Area Sungai Mahakam)** (Buka Sekarang)\n   - View sungai Mahakam dan Jembatan Mahakam\n   - Area foodcourt dengan banyak pilihan makanan\n   - Ada charging station\n   - Lokasi: Jl. Untung Suropati (belakang McD drive thru)\n   - Jam: 15:00 - 22:00\n\nF3 Coffe & City View sangat saya rekomendasikan untuk nongkrong sore karena viewnya memang juara, apalagi pas sunset!",
  "restaurants": [
    {
      "nama_tempat": "F3 Coffe & City View",
      "ringkasan": "F3 Coffe & City View adalah kafe di Samarinda yang menawarkan pemandangan kota yang menakjubkan, ideal untuk nongkrong sore dan malam minggu.",
      "kategori_makanan": "Kopi & Cafe",
      "range_harga": "Variatif",
      "link_lokasi": "https://maps.google.com/...",
      "link_instagram": "https://www.instagram.com/p/C05W5yMP03j/",
      "jam_buka": "10:00",
      "jam_tutup": "23:00",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Ayam Saus Mentega", "Bulgogi", "Pisang Keju", "Kopi Pandan"],
      "fasilitas": ["city_view", "outdoor", "musholla"]
    }
  ]
}
```

### 4. Conversation with Context

**Request 1:**
```json
{
  "message": "Halo, saya lagi cari tempat makan malam",
  "conversation_history": []
}
```

**Response 1:**
```json
{
  "message": "Halo! Selamat malam, saat ini jam 19:15 WITA. Saya siap membantu carikan tempat makan malam yang pas untuk kamu. \n\nBiar saya bisa kasih rekomendasi yang lebih sesuai, boleh kasih tau preferensi kamu:\n- Budget berapa?\n- Pengen makan apa? (Ayam, seafood, Jepang, tradisional, dll)\n- Lokasi yang diinginkan?\n- Ada kebutuhan khusus? (WiFi, tempat luas, view bagus, dll)\n\nAtau kalau mau langsung rekomendasi umum juga bisa!",
  "restaurants": []
}
```

**Request 2:**
```json
{
  "message": "Budget 50 ribuan, pengen yang ada menu ayam, kalau bisa yang ada WiFi buat kerja sambil makan",
  "conversation_history": [
    {
      "role": "user",
      "content": "Halo, saya lagi cari tempat makan malam"
    },
    {
      "role": "assistant",
      "content": "Halo! Selamat malam, saat ini jam 19:15 WITA..."
    }
  ]
}
```

**Response 2:**
```json
{
  "message": "Perfect! Untuk budget 50 ribuan dengan menu ayam dan WiFi, saya punya rekomendasi yang pas:\n\n1. **Kedai Uncle Tao** (Buka Sekarang)\n   - Menu ayam suwir dengan sambal matah yang enak banget\n   - Harga sangat terjangkau mulai 8 ribu (jauh di bawah budget!)\n   - Ada WiFi dan suasana cozy, cocok untuk kerja\n   - Buka sampai jam 22:00\n   - Lokasi: Jl. Ery Suparjan, Perumahan TVRI\n\n2. **Mentimun Resto** (Buka Sekarang)\n   - Prasmanan dengan banyak pilihan lauk ayam\n   - Budget pas di range 50 ribuan\n   - Tempat luas dengan indoor seating\n   - Lokasi: Jl. Belatuk, dekat Hotel Botanic\n\nKedua tempat ini sedang buka dan cocok untuk kerja sambil makan. Kedai Uncle Tao lebih santai dan budget friendly, sementara Mentimun Resto lebih formal dengan pilihan menu lebih banyak. Mana yang lebih menarik?",
  "restaurants": [
    {
      "nama_tempat": "kedai @kedaiuncletao",
      "ringkasan": "Kedai murah meriah dengan WiFi dan suasana cozy",
      "kategori_makanan": "Ayam & Sambal",
      "range_harga": "Murah (<20k)",
      "link_lokasi": "https://maps.google.com/...",
      "link_instagram": "https://www.instagram.com/p/DNrq0sSZP9F/",
      "jam_buka": "10:00",
      "jam_tutup": "22:00",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Sambal Matah", "Ayam Suwir"],
      "fasilitas": ["wifi", "cozy"]
    },
    {
      "nama_tempat": "Mentimun Resto",
      "ringkasan": "Resto prasmanan dengan berbagai pilihan masakan rumahan",
      "kategori_makanan": "Sarapan Banjar",
      "range_harga": "Menengah (20k-50k)",
      "link_lokasi": "https://maps.google.com/...",
      "link_instagram": "https://www.instagram.com/p/DN21YAGZCq-/",
      "jam_buka": "11:00",
      "jam_tutup": "22:00",
      "status_operasional": "Buka Sekarang",
      "menu_andalan": ["Masakan Prasmanan"],
      "fasilitas": ["indoor", "outdoor"]
    }
  ]
}
```

### 5. Closed Restaurant Handling

**Request:**
```json
{
  "message": "Pengen makan di F3 Coffee nih",
  "conversation_history": []
}
```

**Response (if closed):**
```json
{
  "message": "F3 Coffe & City View memang tempat yang bagus! Tapi sayangnya saat ini (jam 01:30 WITA) mereka sudah tutup. Mereka buka dari jam 10:00 - 23:00, jadi akan buka lagi dalam 8 jam.\n\nKalau kamu butuh rekomendasi tempat lain yang buka sekarang untuk makan malam, saya bisa bantu carikan. Atau mau saya ingatkan untuk besok ke F3 Coffee?",
  "restaurants": []
}
```

## Common Use Cases

### 1. Time-Based Recommendations
- Sarapan (05:00 - 10:00)
- Makan siang (10:00 - 15:00)
- Cemilan sore (15:00 - 18:00)
- Makan malam (18:00 - 22:00)

### 2. Budget Filtering
- Murah (<20k)
- Menengah (20k-50k)
- Variatif

### 3. Category Search
- Japanese Food
- Ayam & Sambal
- Kopi & Cafe
- Street Food
- Fast Food
- Sarapan Banjar

### 4. Facility Requirements
- WiFi
- Outdoor seating
- City view
- Musholla
- Charging station
- Indoor/outdoor

### 5. Location-Based
- Dekat Unmul
- Area Sungai Mahakam
- Lokalaya
- Jl. Teuku Umar
- dll.

## Frontend Integration Tips

### Display Restaurant Cards

```javascript
// Example React component
function RestaurantCard({ restaurant }) {
  return (
    <div className="restaurant-card">
      <h3>{restaurant.nama_tempat}</h3>
      <p className="status">{restaurant.status_operasional}</p>
      <p className="description">{restaurant.ringkasan}</p>
      
      <div className="details">
        <span className="category">{restaurant.kategori_makanan}</span>
        <span className="price">{restaurant.range_harga}</span>
      </div>
      
      {restaurant.menu_andalan.length > 0 && (
        <div className="menu">
          <strong>Menu:</strong> {restaurant.menu_andalan.join(', ')}
        </div>
      )}
      
      <div className="actions">
        <a href={restaurant.link_instagram} target="_blank">
          <button>Instagram</button>
        </a>
        <a href={restaurant.link_lokasi} target="_blank">
          <button>Google Maps</button>
        </a>
      </div>
    </div>
  );
}
```

### Handle Conversation History

```javascript
const [messages, setMessages] = useState([]);

async function sendMessage(userMessage) {
  // Add user message
  const newMessages = [...messages, { role: 'user', content: userMessage }];
  setMessages(newMessages);
  
  // Call API
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userMessage,
      conversation_history: messages
    })
  });
  
  const data = await response.json();
  
  // Add assistant response
  setMessages([
    ...newMessages,
    { role: 'assistant', content: data.message }
  ]);
  
  // Display restaurant cards
  setRestaurants(data.restaurants);
}
```

## Error Handling

### Handle API Errors

```javascript
try {
  const response = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const data = await response.json();
  return data;
  
} catch (error) {
  console.error('Error:', error);
  // Show user-friendly error message
  showError('Maaf, terjadi kesalahan. Silakan coba lagi.');
}
```

## Performance Tips

1. **Debounce user input** - Don't send request on every keystroke
2. **Show loading state** - Display spinner while waiting for response
3. **Cache responses** - Cache common queries on frontend
4. **Lazy load images** - If showing restaurant images
5. **Pagination** - If showing many restaurants
