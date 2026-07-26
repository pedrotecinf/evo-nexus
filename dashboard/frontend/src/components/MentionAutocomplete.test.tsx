import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import MentionAutocomplete, { mentionMenuGeometry } from './MentionAutocomplete'

const context = { start: 0, end: 2, query: 'a' }
const agents = [
  { name: 'atlas-project', description: 'Projetos', locked: false },
  { name: 'vault-security', description: 'Segurança', locked: true },
]

describe('MentionAutocomplete', () => {
  it('mostra opções selecionáveis, omite locked e permite clique', () => {
    const onSelect = vi.fn()
    render(<MentionAutocomplete agents={agents} error={false} context={context} assignee="atlas-project" selectedIndex={0} onSelect={onSelect} onSelectedIndexChange={vi.fn()} anchorRef={{ current: null }} listboxId="mentions" />)
    expect(screen.getByRole('listbox')).toBeInTheDocument()
    expect(screen.getByRole('option', { name: /@atlas-project/i })).toHaveAttribute('aria-selected', 'true')
    expect(screen.queryByText('@vault-security')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('option', { name: /@atlas-project/i }))
    expect(onSelect).toHaveBeenCalledWith(agents[0])
  })

  it('mostra loading, erro e vazio', () => {
    const props = { context, assignee: null, selectedIndex: 0, onSelect: vi.fn(), onSelectedIndexChange: vi.fn(), anchorRef: { current: null }, listboxId: 'mentions' }
    const { rerender } = render(<MentionAutocomplete {...props} agents={null} error={false} />)
    expect(screen.getByText('Carregando agentes...')).toBeInTheDocument()
    rerender(<MentionAutocomplete {...props} agents={null} error />)
    expect(screen.getByText('Não foi possível carregar agentes.')).toBeInTheDocument()
    rerender(<MentionAutocomplete {...props} agents={[]} error={false} />)
    expect(screen.getByText('Nenhum agente disponível.')).toBeInTheDocument()
  })

  it('calcula direção acima ou abaixo conforme espaço disponível', () => {
    Object.defineProperty(window, 'innerHeight', { value: 500, configurable: true })
    expect(mentionMenuGeometry({ top: 260, bottom: 480 } as DOMRect)).toEqual({ direction: 'above', maxHeight: 224 })
    expect(mentionMenuGeometry({ top: 20, bottom: 100 } as DOMRect)).toEqual({ direction: 'below', maxHeight: 224 })
    expect(mentionMenuGeometry({ top: 10, bottom: 490 } as DOMRect)).toEqual({ direction: 'below', maxHeight: 0 })
  })
})
