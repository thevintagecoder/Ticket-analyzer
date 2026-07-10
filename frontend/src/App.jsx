import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function App() {
  const [tickets, setTickets] = useState([]);

  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [category, setCategory] = useState("");

  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function fetchTickets() {
    try {
      setIsLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/tickets`);

      if (!response.ok) {
        throw new Error("Could not load tickets.");
      }

      const data = await response.json();
      setTickets(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!title.trim() || !message.trim()) {
      setError("Title and message are required.");
      return;
    }

    const ticketData = {
      title: title.trim(),
      message: message.trim(),
      category: category.trim() || null,
    };

    try {
      setIsSubmitting(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/tickets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(ticketData),
      });

      if (!response.ok) {
        throw new Error("Could not submit ticket.");
      }

      setTitle("");
      setMessage("");
      setCategory("");

      await fetchTickets();
    } catch (err) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  useEffect(() => {
    fetchTickets();
  }, []);

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Ticket Analyzer</p>
        <h1>Analyze support tickets with AI</h1>
        <p className="subtitle">
          Submit a ticket, detect whether it is positive or negative, and save
          it in PostgreSQL.
        </p>
      </section>

      <section className="layout">
        <form className="card form-card" onSubmit={handleSubmit}>
          <h2>Submit a ticket</h2>

          <label htmlFor="title">Title</label>
          <input
            id="title"
            type="text"
            placeholder="Lab VM issue"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
          />

          <label htmlFor="message">Message</label>
          <textarea
            id="message"
            rows="6"
            placeholder="My lab VM is not opening before the deadline."
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />

          <label htmlFor="category">Category optional</label>
          <input
            id="category"
            type="text"
            placeholder="lab"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          />

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Analyzing..." : "Submit ticket"}
          </button>

          {error && <p className="error">{error}</p>}
        </form>

        <section className="card list-card">
          <div className="list-header">
            <h2>Saved tickets</h2>
            <button
              type="button"
              className="secondary-button"
              onClick={fetchTickets}
            >
              Refresh
            </button>
          </div>

          {isLoading ? (
            <p className="muted">Loading tickets...</p>
          ) : tickets.length === 0 ? (
            <p className="muted">No tickets submitted yet.</p>
          ) : (
            <div className="ticket-list">
              {tickets.map((ticket) => (
                <article className="ticket" key={ticket.id}>
                  <div className="ticket-top">
                    <h3>{ticket.title}</h3>

                    <span
                      className={
                        ticket.sentiment === "POSITIVE"
                          ? "badge positive"
                          : "badge negative"
                      }
                    >
                      {ticket.sentiment}
                    </span>
                  </div>

                  <p>{ticket.message}</p>

                  <div className="ticket-meta">
                    <span>Category: {ticket.category || "None"}</span>
                    <span>
                      Confidence: {(ticket.confidence * 100).toFixed(1)}%
                    </span>
                  </div>

                  <small>
                    Created: {new Date(ticket.created_at).toLocaleString()}
                  </small>
                </article>
              ))}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
