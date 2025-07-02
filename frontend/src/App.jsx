import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
    <div className="p-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Semantic Painting Search</h1>
      <p>Ready to connect to your backend API.</p>
    </div>
    </>
  )
}

export default App
