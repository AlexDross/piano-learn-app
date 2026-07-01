import { Routes, Route, NavLink } from 'react-router-dom'
import LibraryPage from './pages/LibraryPage'
import SongDetailPage from './pages/SongDetailPage'
import AddSongPage from './pages/AddSongPage'
import FavoritesPage from './pages/FavoritesPage'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🎹 Piano Learn</h1>
        <nav className="app-nav">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link nav-link-active' : 'nav-link'}>
            Library
          </NavLink>
          <NavLink to="/favorites" className={({ isActive }) => isActive ? 'nav-link nav-link-active' : 'nav-link'}>
            Favorites
          </NavLink>
          <NavLink to="/add" className={({ isActive }) => isActive ? 'nav-link nav-link-active' : 'nav-link'}>
            Add Song
          </NavLink>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<LibraryPage />} />
          <Route path="/favorites" element={<FavoritesPage />} />
          <Route path="/song/:id" element={<SongDetailPage />} />
          <Route path="/add" element={<AddSongPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
