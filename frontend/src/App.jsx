import { useState } from 'react'
import SearchView from './pages/SearchView.jsx'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <SearchView />
    </>
  )
}

export default App
