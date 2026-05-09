import { useState, useRef, useEffect } from "react";

const PERSONAS = [
  {
    id: "storonsky",
    name: "Николай Сторонский",
    role: "Основатель Revolut ($75B)",
    emoji: "💳",
    color: "#00D4AA",
    bg: "#001A15",
    systemPrompt: `Ты — Николай Сторонский, основатель и CEO Revolut. 

ТВОЯ ЛИЧНОСТЬ И МЫШЛЕНИЕ:
- Физик по образованию (МФТИ) + экономист (РЭШ) — структурное, логическое, абстрактное мышление
- Бывший трейдер в Lehman Brothers, Credit Suisse — привык к риску и скорости
- Построил компанию $75 млрд из личных £300K накоплений
- Принцип: "Страшно потерять жизнь и здоровье, деньги — нет"
- KPI-driven: всё измеримо, метрики важнее политики
- Ненавидишь бюрократию и "corporate BS"
- Нанимаешь только "достигаторов" — людей, готовых жертвовать балансом work/life
- Веришь в группы 5-6 умных, ego-free людей для принятия решений
- Ценишь: логическое мышление, открытость к новым идеям, готовность ошибаться
- "Нападение лучше защиты" — агрессивная экспансия, скорость важнее осторожности
- Автоматизация — ключ к масштабу (80% процессов Revolut автоматизированы)
- Техническое образование обязательно для основателя tech-компании

СТИЛЬ ОБЩЕНИЯ:
- Прямой, без воды, конкретный
- Говоришь по-русски, иногда вставляешь английские термины (KPI-driven, pattern recognition, scale)
- Не любишь пустые слова, требуешь конкретики
- Мыслишь системно: проблема → метрика → решение → масштаб
- Короткие, чёткие фразы. Без лирики.

Отвечай как Николай Сторонский — со своей уникальной перспективой финтех-основателя. 2-4 предложения. Будь конкретным и немного жёстким.`,
  },
  {
    id: "musk",
    name: "Илон Маск",
    role: "Tesla, SpaceX, X — $300B+",
    emoji: "🚀",
    color: "#E8C547",
    bg: "#1A1500",
    systemPrompt: `Ты — Илон Маск, основатель Tesla, SpaceX, X, Neuralink.

ТВОЯ ЛИЧНОСТЬ И МЫШЛЕНИЕ:
- First Principles Thinking: разбивай всё до базовых физических истин, строй заново
- "Любой план, который не провалился хотя бы раз — недостаточно амбициозен"
- Работаешь 80-100 часов в неделю, требуешь того же от команды
- Многозадачность: CEO 6+ компаний одновременно
- Ненавидишь бессмысленные встречи — выходишь с них или отменяешь
- Рискуешь всем: вложил последние деньги в Tesla и SpaceX в 2008 одновременно
- Думаешь в масштабах: не "улучшить такси", а "переселить человечество на Марс"
- Ускорение — твой главный принцип: делай быстро, ошибайся, итерируй
- Критик "MBA-мышления": бизнес-школы учат оптимизировать, а не создавать
- Верит в меритократию и прозрачность

СТИЛЬ: саркастичный, прямой, иногда мемный. Мыслишь экстремально масштабно. 2-4 предложения.`,
  },
  {
    id: "krivenko",
    name: "Андрей Кривенко",
    role: "Основатель ВкусВилл ($2.1B)",
    emoji: "🥦",
    color: "#7BC67E",
    bg: "#071209",
    systemPrompt: `Ты — Андрей Кривенко, основатель и идеолог ВкусВилл, создатель системы управления Beyond Taylor, основатель фонда ТилТех.

ТВОЯ ЛИЧНОСТЬ И МЫШЛЕНИЕ:
- Вырос в семье физиков в Черноголовке, окончил МФТИ (физико-биологический факультет) — аналитик до мозга костей
- Начал с 16 000 рублей и 6 позиций в ассортименте, без внешних инвестиций
- Главный принцип жизни и бизнеса: ДОВЕРИЕ — клиентам, сотрудникам, поставщикам
- Клиентократия: клиент — смысл работы, всё остальное вторично. Если делаешь что-то бесполезное для покупателя — зачем вообще это делаешь?
- "Бизнесом нельзя владеть. Бизнес — это идея, которая помогает делать жизнь людей лучше"
- Деньги — лишь способ достижения цели, не цель сама по себе
- Beyond Taylor: никаких начальников, планов и регламентов — только самоуправляемые команды
- Нет рекламы — только качество. "Реклама означает, что не могут продать"
- Минимум активов: всё, что можно — в аренду, не в собственность
- Продавцов не штрафуют, а премируют за нахождение проблем
- Сам не занимался операционкой: не знает как открыть магазин, не был в дарксторе, у поставщиков не был 15 лет — и это правильно
- Инвестирует в людей с которыми "приятно пойти в ресторан" — человеческий фактор важнее цифр

СТИЛЬ ОБЩЕНИЯ:
- Тихий, вдумчивый, философский. Говорит медленно и по существу.
- Задаёт встречные вопросы: "А зачем? Кому это нужно?"
- Говорит о доверии, смысле, людях — не о деньгах и метриках
- Русский язык, простые слова, без пафоса
- Иногда признаётся: "Я не знаю" или "Это не моя область"

Отвечай как Андрей Кривенко. 2-4 предложения. Через призму доверия, клиента и смысла.`,
  },
  {
    id: "bezos",
    name: "Джефф Безос",
    role: "Основатель Amazon ($2T+)",
    emoji: "📦",
    color: "#FF9900",
    bg: "#1A0D00",
    systemPrompt: `Ты — Джефф Безос, основатель Amazon, Blue Origin, владелец Washington Post.

ТВОЯ ЛИЧНОСТЬ И МЫШЛЕНИЕ:
- Customer Obsession — одержимость клиентом превыше всего. "Конкуренты не платят нам зарплату — платят клиенты"
- Day 1 философия: всегда действуй как стартап в первый день. Day 2 = стагнация, смерть
- Долгосрочное мышление: Wall Street хочет квартальных результатов — ты строишь на 10-20 лет вперёд
- Work backwards: начинай с press release — что ты хочешь объявить клиенту? Затем строй обратно
- "Два вида компаний: те, кто работает чтобы брать больше, и те, кто работает чтобы брать меньше. Мы — вторые"
- Высочайшие стандарты: "Я лучше проведу 50 интервью и не найму никого, чем найму не того человека"
- Disagree and Commit: открыто не соглашайся, но после решения — 100% commitment
- Изобретение и эксперимент: провал — неотъемлемая часть инновации. Нет эксперимента — нет роста
- Frugality: ограничения рождают изобретательность. Меньше ресурсов = больше креативности
- Think Big: "Большие дубы начинаются с жёлудя. Будь готов дать жёлудю вырасти"
- Ждёт до конца встречи, чтобы высказать своё мнение — чтобы не давить на команду
- Письма акционерам — главный инструмент коммуникации культуры

СТИЛЬ ОБЩЕНИЯ:
- Аналитичный, методичный, терпеливый
- Говорит притчами и метафорами ("Day 1", "жёлудь", "работать с клиентом")
- Задаёт вопросы вглубь: "А что хочет клиент на самом деле?"
- Принципиальный, но не агрессивный
- Иногда саркастичен по отношению к краткосрочному мышлению

Отвечай как Джефф Безос. 2-4 предложения. Через призму клиента, долгосрочности и изобретения.`,
  },
];

const MODERATOR_PROMPT = `Ты — модератор совета успешных людей. Твоя задача: кратко (1-2 предложения) подвести итог дискуссии между Николаем Сторонским, Илоном Маском, Андреем Кривенко и Джеффом Безосом по проблеме пользователя. Выдели главный инсайт и конкретный первый шаг. Говори по-русски.`;

export default function AICouncil() {
  const [problem, setProblem] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentSpeaker, setCurrentSpeaker] = useState(null);
  const [summary, setSummary] = useState("");
  const [phase, setPhase] = useState("input"); // input | discussing | summary
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, summary]);

  const callClaude = async (systemPrompt, userMessage, conversationHistory = []) => {
    const msgs = [
      ...conversationHistory,
      { role: "user", content: userMessage }
    ];
    try {
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 300,
          system: systemPrompt,
          messages: msgs,
        }),
      });
      if (!response.ok) {
        const err = await response.text();
        console.error("API error:", response.status, err);
        return "⚠️ Ошибка API. Попробуй ещё раз.";
      }
      const data = await response.json();
      return data.content?.[0]?.text || "Нет ответа";
    } catch (e) {
      console.error("Fetch error:", e);
      return "⚠️ Ошибка соединения.";
    }
  };

  const runDiscussion = async () => {
    if (!problem.trim()) return;
    setPhase("discussing");
    setLoading(true);
    setMessages([]);
    setSummary("");

    const history = [];
    const addMsg = (persona, text) => {
      setMessages(prev => [...prev, { persona, text }]);
    };

    try {
      addMsg({ name: "Совет", emoji: "⏳", color: "#888", bg: "#111", role: "загружаю..." }, "Подключаюсь к экспертам... подожди ~30 секунд");
      await new Promise(r => setTimeout(r, 800));
      setMessages([]);

      // Round 1: each person responds to the problem
      for (const persona of PERSONAS) {
        setCurrentSpeaker(persona.id);
        const prompt = `Проблема пользователя: "${problem}"\n\nДай своё мнение как ${persona.name}. Что ты думаешь об этой проблеме и как бы её решил? 2-3 предложения.`;
        const reply = await callClaude(persona.systemPrompt, prompt);
        addMsg(persona, reply);
        history.push({ role: "assistant", content: `${persona.name}: ${reply}` });
        await new Promise(r => setTimeout(r, 300));
      }

      // Round 2: cross-discussion
      for (let i = 0; i < PERSONAS.length; i++) {
        const persona = PERSONAS[i];
        const others = PERSONAS.filter((_, j) => j !== i).map(p => p.name).join(", ");
        setCurrentSpeaker(persona.id);
        const discussionContext = history.map(h => h.content).join("\n");
        const prompt = `Проблема: "${problem}"\n\nВот что сказали ${others}:\n${discussionContext}\n\nОтреагируй на их идеи как ${persona.name}. С чем согласен, с чем нет? Добавь свою конкретную рекомендацию. 2-3 предложения.`;
        const reply = await callClaude(persona.systemPrompt, prompt);
        addMsg(persona, reply);
        history.push({ role: "assistant", content: `${persona.name} (раунд 2): ${reply}` });
        await new Promise(r => setTimeout(r, 300));
      }

      // Final summary
      setCurrentSpeaker("moderator");
      const fullDiscussion = history.map(h => h.content).join("\n\n");
      const summaryText = await callClaude(
        MODERATOR_PROMPT,
        `Проблема: "${problem}"\n\nДискуссия:\n${fullDiscussion}\n\nПодведи итог.`
      );
      setSummary(summaryText);
      setPhase("summary");
    } catch (e) {
      console.error(e);
    } finally {
      setCurrentSpeaker(null);
      setLoading(false);
    }
  };

  const reset = () => {
    setPhase("input");
    setProblem("");
    setMessages([]);
    setSummary("");
    setCurrentSpeaker(null);
    setLoading(false);
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#080808",
      color: "#E8E8E8",
      fontFamily: "'Georgia', serif",
      padding: "0",
    }}>
      {/* Header */}
      <div style={{
        borderBottom: "1px solid #222",
        padding: "24px 32px",
        display: "flex",
        alignItems: "center",
        gap: "16px",
        background: "#0A0A0A",
      }}>
        <div style={{ fontSize: "32px" }}>🧠</div>
        <div>
          <div style={{ fontSize: "20px", fontWeight: "700", letterSpacing: "0.5px", color: "#fff" }}>
            Совет Умов
          </div>
          <div style={{ fontSize: "12px", color: "#666", letterSpacing: "1px", textTransform: "uppercase", fontFamily: "monospace" }}>
            AI Council of Successful Minds
          </div>
        </div>
      </div>

      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "32px 24px" }}>

        {/* Personas Preview */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "32px" }}>
          {PERSONAS.map(p => (
            <div key={p.id} style={{
              background: p.bg,
              border: `1px solid ${p.color}22`,
              borderLeft: `3px solid ${p.color}`,
              borderRadius: "8px",
              padding: "12px 16px",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              opacity: currentSpeaker === p.id ? 1 : currentSpeaker ? 0.4 : 1,
              transition: "opacity 0.3s",
              boxShadow: currentSpeaker === p.id ? `0 0 20px ${p.color}33` : "none",
            }}>
              <div style={{ fontSize: "24px" }}>{p.emoji}</div>
              <div>
                <div style={{ fontSize: "13px", fontWeight: "700", color: p.color }}>{p.name}</div>
                <div style={{ fontSize: "11px", color: "#666", fontFamily: "monospace" }}>{p.role}</div>
              </div>
              {currentSpeaker === p.id && (
                <div style={{ marginLeft: "auto", display: "flex", gap: "3px" }}>
                  {[0,1,2].map(i => (
                    <div key={i} style={{
                      width: "4px", height: "4px", borderRadius: "50%",
                      background: p.color,
                      animation: `pulse 1s ${i * 0.2}s infinite`,
                    }} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input Phase */}
        {phase === "input" && (
          <div>
            <div style={{ marginBottom: "8px", fontSize: "14px", color: "#888", fontFamily: "monospace" }}>
              // Опиши свою проблему или вопрос
            </div>
            <textarea
              value={problem}
              onChange={e => setProblem(e.target.value)}
              placeholder="Например: Я хочу запустить стартап, но боюсь уйти с работы. Как мне понять, готов ли я к этому шагу?"
              rows={4}
              style={{
                width: "100%",
                background: "#111",
                border: "1px solid #333",
                borderRadius: "8px",
                color: "#E8E8E8",
                fontSize: "15px",
                padding: "16px",
                resize: "vertical",
                outline: "none",
                fontFamily: "Georgia, serif",
                lineHeight: "1.6",
                boxSizing: "border-box",
              }}
              onFocus={e => e.target.style.borderColor = "#555"}
              onBlur={e => e.target.style.borderColor = "#333"}
            />
            <button
              onClick={runDiscussion}
              disabled={!problem.trim()}
              style={{
                marginTop: "16px",
                width: "100%",
                padding: "16px",
                background: problem.trim() ? "#00D4AA" : "#1A1A1A",
                color: problem.trim() ? "#000" : "#444",
                border: "none",
                borderRadius: "8px",
                fontSize: "15px",
                fontWeight: "700",
                cursor: problem.trim() ? "pointer" : "not-allowed",
                transition: "all 0.2s",
                letterSpacing: "0.5px",
              }}
            >
              Запустить Совет Умов →
            </button>
            <div style={{ marginTop: "12px", fontSize: "12px", color: "#444", textAlign: "center", fontFamily: "monospace" }}>
              4 эксперта × 2 раунда дискуссии + итоговый вывод
            </div>
          </div>
        )}

        {/* Discussion Phase */}
        {(phase === "discussing" || phase === "summary") && (
          <div>
            <div style={{ marginBottom: "20px", padding: "16px", background: "#111", borderRadius: "8px", border: "1px solid #222" }}>
              <div style={{ fontSize: "11px", color: "#555", fontFamily: "monospace", marginBottom: "6px" }}>ПРОБЛЕМА</div>
              <div style={{ fontSize: "14px", color: "#CCC", lineHeight: "1.5" }}>"{problem}"</div>
            </div>

            {/* Messages */}
            <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {messages.map((msg, idx) => (
                <div key={idx} style={{
                  background: msg.persona.bg,
                  border: `1px solid ${msg.persona.color}22`,
                  borderLeft: `3px solid ${msg.persona.color}`,
                  borderRadius: "8px",
                  padding: "16px",
                  animation: "fadeIn 0.4s ease",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px" }}>
                    <span style={{ fontSize: "18px" }}>{msg.persona.emoji}</span>
                    <div>
                      <div style={{ fontSize: "13px", fontWeight: "700", color: msg.persona.color }}>
                        {msg.persona.name}
                      </div>
                      <div style={{ fontSize: "11px", color: "#555", fontFamily: "monospace" }}>
                        {msg.persona.role}
                      </div>
                    </div>
                  </div>
                  <div style={{ fontSize: "14px", lineHeight: "1.7", color: "#CCC" }}>
                    {msg.text}
                  </div>
                </div>
              ))}

              {/* Loading indicator */}
              {loading && currentSpeaker && (
                <div style={{
                  background: "#111",
                  border: "1px solid #222",
                  borderRadius: "8px",
                  padding: "16px",
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                }}>
                  {(() => {
                    const p = currentSpeaker === "moderator"
                      ? { emoji: "⚡", name: "Модератор", color: "#FFD700" }
                      : PERSONAS.find(x => x.id === currentSpeaker);
                    return p ? (
                      <>
                        <span style={{ fontSize: "18px" }}>{p.emoji}</span>
                        <span style={{ fontSize: "13px", color: p.color }}>{p.name}</span>
                        <span style={{ fontSize: "12px", color: "#555", fontFamily: "monospace" }}>думает...</span>
                      </>
                    ) : null;
                  })()}
                </div>
              )}

              {/* Summary */}
              {summary && (
                <div style={{
                  background: "linear-gradient(135deg, #0D1A0D, #0A0A1A)",
                  border: "1px solid #00D4AA44",
                  borderRadius: "12px",
                  padding: "20px",
                  animation: "fadeIn 0.5s ease",
                }}>
                  <div style={{ fontSize: "11px", color: "#00D4AA", fontFamily: "monospace", marginBottom: "10px", letterSpacing: "1px" }}>
                    ⚡ ИТОГОВЫЙ ВЫВОД СОВЕТА
                  </div>
                  <div style={{ fontSize: "15px", lineHeight: "1.7", color: "#E8E8E8" }}>
                    {summary}
                  </div>
                </div>
              )}
            </div>

            {phase === "summary" && (
              <button
                onClick={reset}
                style={{
                  marginTop: "24px",
                  width: "100%",
                  padding: "14px",
                  background: "transparent",
                  color: "#666",
                  border: "1px solid #333",
                  borderRadius: "8px",
                  fontSize: "14px",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
                onMouseEnter={e => { e.target.style.borderColor = "#555"; e.target.style.color = "#999"; }}
                onMouseLeave={e => { e.target.style.borderColor = "#333"; e.target.style.color = "#666"; }}
              >
                ← Новый вопрос
              </button>
            )}

            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(0.8); }
          50% { opacity: 1; transform: scale(1.2); }
        }
        textarea::placeholder { color: #444; }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  );
}
