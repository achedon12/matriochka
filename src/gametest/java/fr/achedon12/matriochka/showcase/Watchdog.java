package fr.achedon12.matriochka.showcase;

import fr.achedon12.matriochka.Matriochka;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.core.LogEvent;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.AbstractAppender;
import org.apache.logging.log4j.core.config.Property;

/**
 * Ends a test run the moment the game breaks in a way the test thread never sees: a chunk that fails to generate,
 * a data file that does not load, a crashed server thread. Without it, the test waits forever on a chunk that will
 * never come. Also ends a run in which nothing has been logged for a long time (a hang).
 */
final class Watchdog {
	private Watchdog() {}

	/** Error lines that mean the run cannot go on. */
	private static final String[] FATAL = {
		"Exception generating new chunk", "Missing element", "Couldn't parse data file", "Failed to load datapacks",
		"Encountered an unexpected exception", "This crash report has been saved"
	};
	private static final long QUIET_MS = Long.getLong("matriochka.watchdog.quiet", 240_000L);
	private static volatile long last = System.currentTimeMillis();
	private static boolean started;

	static synchronized void start() {
		if (started) return;
		started = true;
		LoggerContext lc = (LoggerContext) LogManager.getContext(false);
		AbstractAppender app = new AbstractAppender("matriochka-watchdog", null, null, true, Property.EMPTY_ARRAY) {
			@Override
			public void append(LogEvent e) {
				last = System.currentTimeMillis();
				if (!e.getLevel().isMoreSpecificThan(Level.ERROR)) return;
				String m = e.getMessage().getFormattedMessage();
				Throwable t = e.getThrown();
				StringBuilder all = new StringBuilder(m == null ? "" : m);
				for (Throwable c = t; c != null; c = c.getCause()) all.append(' ').append(c);
				for (String f : FATAL) if (all.indexOf(f) >= 0) halt("fatal error: " + all);
			}
		};
		app.start();
		lc.getConfiguration().getRootLogger().addAppender(app, Level.ALL, null);
		lc.updateLoggers();
		Thread t = new Thread(() -> {
			while (true) {
				try {
					Thread.sleep(10_000);
				} catch (InterruptedException e) {
					return;
				}
				if (System.currentTimeMillis() - last > QUIET_MS) halt("nothing logged for " + QUIET_MS / 1000 + " s, the run is stuck");
			}
		}, "matriochka-watchdog");
		t.setDaemon(true);
		t.start();
	}

	/** Marks the run alive: a long quiet step (a fight, a long wait) calls this from the test thread. */
	static void alive() {
		last = System.currentTimeMillis();
	}

	private static void halt(String why) {
		String line = "[watchdog] " + (why.length() > 2000 ? why.substring(0, 2000) : why);
		System.err.println(line);
		Matriochka.LOG.error(line);
		System.err.flush();
		System.out.flush();
		Runtime.getRuntime().halt(3);
	}
}
