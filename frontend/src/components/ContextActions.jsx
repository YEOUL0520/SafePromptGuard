import { downloadText, buildCollabSummary, GIT_CHECKLIST, SHARE_CHECKLIST } from '../utils/export'

function NotebookDownloadButton({ result }) {
  if (!result?.masked_notebook_json) return null
  return (
    <button
      type="button"
      className="msg-btn"
      onClick={() => downloadText('masked_notebook.ipynb', result.masked_notebook_json)}
    >
      마스킹 노트북 (.ipynb)
    </button>
  )
}

export default function ContextActions({ contextId, result, onCopy }) {
  if (!result) return null

  const masked = result.masked_text || ''
  const notebookBtn = <NotebookDownloadButton result={result} />

  if (contextId === 'git') {
    return (
      <div className="context-actions">
        <button
          type="button"
          className="msg-btn msg-btn--primary"
          onClick={() => downloadText('masked_for_commit.txt', masked)}
        >
          마스킹 파일 저장
        </button>
        <button
          type="button"
          className="msg-btn"
          onClick={() => onCopy(GIT_CHECKLIST, '체크리스트')}
        >
          커밋 전 체크리스트 복사
        </button>
        {notebookBtn}
      </div>
    )
  }

  if (contextId === 'share' || contextId === 'other') {
    return (
      <div className="context-actions">
        <button
          type="button"
          className="msg-btn msg-btn--primary"
          onClick={() => downloadText('masked_share.txt', masked)}
        >
          마스킹 파일 저장
        </button>
        <button
          type="button"
          className="msg-btn"
          onClick={() => onCopy(SHARE_CHECKLIST, '체크리스트')}
        >
          공유 전 체크리스트 복사
        </button>
        {notebookBtn}
      </div>
    )
  }

  if (contextId === 'collab') {
    const summary = buildCollabSummary(result)
    return (
      <div className="context-actions">
        <button
          type="button"
          className="msg-btn msg-btn--primary"
          onClick={() => onCopy(summary, '협업용 요약')}
        >
          협업 채널용 요약 복사
        </button>
        {notebookBtn}
      </div>
    )
  }

  if (result.masked_notebook_json) {
    return <div className="context-actions">{notebookBtn}</div>
  }

  return null
}
