import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import CommentComposer from './CommentComposer'
import { api } from '../lib/api'

vi.mock('../lib/api', () => ({ api: { get: vi.fn() } }))

const getAgents = vi.mocked(api.get)
const agents = [
  { name: 'atlas-project', description: 'Projetos', locked: false },
  { name: 'zara-cs', description: 'Suporte', locked: false },
  { name: 'vault-security', description: 'Segurança', locked: true },
]

describe('CommentComposer', () => {
  it('busca agentes somente ao abrir contexto e permite teclado, clique, caret e suffix', async () => {
    const user = userEvent.setup()
    getAgents.mockResolvedValue(agents)
    render(<CommentComposer assignee="zara-cs" submitting={false} onSubmit={vi.fn()} />)
    const textarea = screen.getByRole('combobox') as HTMLTextAreaElement

    expect(getAgents).not.toHaveBeenCalled()
    await user.type(textarea, 'Antes @')
    await waitFor(() => expect(getAgents).toHaveBeenCalledWith('/agents'))
    await screen.findAllByRole('option')
    expect(screen.getAllByRole('option').map(option => option.textContent)).toEqual([
      expect.stringContaining('@zara-cs'),
      expect.stringContaining('@atlas-project'),
    ])
    expect(screen.queryByText('@vault-security')).not.toBeInTheDocument()
    expect(screen.queryByText('@vault-security')).not.toBeInTheDocument()

    fireEvent.keyDown(textarea, { key: 'ArrowDown' })
    fireEvent.keyDown(textarea, { key: 'Enter' })
    await waitFor(() => expect(textarea.value).toBe('Antes @atlas-project'))
    expect(document.activeElement).toBe(textarea)
    expect(textarea.selectionStart).toBe(20)
    await user.clear(textarea)
    await user.type(textarea, '@za')
    await screen.findByRole('option', { name: /@zara-cs/i })
    fireEvent.blur(textarea)
    fireEvent.click(screen.getByRole('option', { name: /@zara-cs/i }))
    await waitFor(() => expect(textarea.value).toBe('@zara-cs'))
  })

  it('fecha em Escape e só declara aria-activedescendant para opção existente', async () => {
    getAgents.mockResolvedValue(agents)
    render(<CommentComposer assignee={null} submitting={false} onSubmit={vi.fn()} />)
    const textarea = screen.getByRole('combobox')
    fireEvent.change(textarea, { target: { value: '@missing', selectionStart: 8 } })
    await waitFor(() => expect(getAgents).toHaveBeenCalled())
    expect(textarea).not.toHaveAttribute('aria-activedescendant')
    fireEvent.keyDown(textarea, { key: 'Escape' })
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument()
  })

  it('expõe loading, erro, vazio e menu abaixo em fluxo ou acima sem sobreposição', async () => {
    getAgents.mockImplementation(() => new Promise(() => {}))
    const { rerender } = render(<CommentComposer assignee={null} submitting={false} onSubmit={vi.fn()} />)
    const textarea = screen.getByRole('combobox')
    fireEvent.change(textarea, { target: { value: '@', selectionStart: 1 } })
    expect(await screen.findByText('Carregando agentes...')).toBeInTheDocument()

    getAgents.mockRejectedValueOnce(new Error('offline'))
    rerender(<CommentComposer assignee={null} submitting={false} onSubmit={vi.fn()} />)
    fireEvent.change(screen.getByRole('combobox'), { target: { value: '@a', selectionStart: 2 } })
    expect(await screen.findByText('Não foi possível carregar agentes.')).toBeInTheDocument()
  })
})
