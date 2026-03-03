import { create } from 'zustand'

const useQueryStore = create((set) => ({
  isLoading: false,
  error: null,
  result: null,
  history: [],
  historyLoading: false,
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setResult: (result) => set({ result }),
  setHistory: (history) => set({ history }),
  setHistoryLoading: (historyLoading) => set({ historyLoading }),
  clearResult: () => set({ result: null, error: null }),
}))

export default useQueryStore