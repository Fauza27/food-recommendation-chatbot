import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
import json

class PostsService:
    def __init__(self, data_path: str = "data/cleaned_enhanced_data_2.csv"):
        """Initialize posts service with CSV data"""
        self.data_path = Path(data_path)
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and prepare restaurant data from CSV"""
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"Loaded {len(self.df)} restaurants from CSV")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def _parse_list_field(self, value) -> List[str]:
        """Parse string representation of list to actual list"""
        if pd.isna(value) or value == "[]":
            return []
        try:
            # Handle string representation of list
            if isinstance(value, str):
                # Remove brackets and quotes, split by comma
                cleaned = value.strip("[]'\"")
                if not cleaned:
                    return []
                items = [item.strip().strip("'\"") for item in cleaned.split("',")]
                return [item for item in items if item]
            return []
        except:
            return []
    
    def _row_to_post(self, row) -> Dict:
        """Convert DataFrame row to post dictionary"""
        return {
            "nama_tempat": str(row.get("nama_tempat", "Unknown")),
            "lokasi": str(row.get("lokasi", "Unknown")),
            "kategori_makanan": str(row.get("kategori_makanan", "Unknown")),
            "tipe_tempat": str(row.get("tipe_tempat", "Unknown")),
            "range_harga": str(row.get("range_harga", "Unknown")),
            "menu_andalan": self._parse_list_field(row.get("menu_andalan", "[]")),
            "fasilitas": self._parse_list_field(row.get("fasilitas", "[]")),
            "jam_buka": str(row.get("jam_buka", "Unknown")),
            "jam_tutup": str(row.get("jam_tutup", "Unknown")),
            "hari_operasional": self._parse_list_field(row.get("hari_operasional", "[]")),
            "ringkasan": str(row.get("ringkasan", "")),
            "tags": self._parse_list_field(row.get("tags", "[]")),
            "url": str(row.get("url", ""))
        }
    
    def get_posts(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict:
        """
        Get paginated posts with optional search and category filter
        
        Args:
            page: Page number (1-indexed)
            limit: Number of items per page
            search: Search query for nama_tempat, lokasi, or ringkasan
            category: Filter by kategori_makanan or tags
        
        Returns:
            Dictionary with posts, pagination info
        """
        if self.df is None or len(self.df) == 0:
            return {
                "posts": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0
            }
        
        # Start with full dataframe
        filtered_df = self.df.copy()
        
        # Apply search filter
        if search and search.strip():
            search_lower = search.lower().strip()
            mask = (
                filtered_df["nama_tempat"].str.lower().str.contains(search_lower, na=False) |
                filtered_df["lokasi"].str.lower().str.contains(search_lower, na=False) |
                filtered_df["ringkasan"].str.lower().str.contains(search_lower, na=False) |
                filtered_df["tags"].str.lower().str.contains(search_lower, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Apply category filter
        if category and category.strip() and category.lower() != "all":
            category_lower = category.lower().strip()
            mask = (
                filtered_df["kategori_makanan"].str.lower().str.contains(category_lower, na=False) |
                filtered_df["tags"].str.lower().str.contains(category_lower, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Calculate pagination
        total = len(filtered_df)
        total_pages = (total + limit - 1) // limit  # Ceiling division
        
        # Get page data
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        # Convert to list of dicts
        posts = [self._row_to_post(row) for _, row in page_df.iterrows()]
        
        return {
            "posts": posts,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    
    def get_categories(self) -> List[str]:
        """Get all unique categories from data"""
        if self.df is None or len(self.df) == 0:
            return []
        
        categories = set()
        
        # Add kategori_makanan
        categories.update(self.df["kategori_makanan"].dropna().unique())
        
        # Add tags
        for tags_str in self.df["tags"].dropna():
            tags = self._parse_list_field(tags_str)
            categories.update(tags)
        
        return sorted(list(categories))
