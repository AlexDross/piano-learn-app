import SongLibrary from '../components/SongLibrary'

export default function FavoritesPage() {
  return (
    <div className="page">
      <h2>Favorites</h2>
      <SongLibrary favoritesOnly />
    </div>
  )
}
