# ==========================================
# Stage 1: Builder
# ==========================================
FROM pgvector/pgvector:pg17 AS builder

# 1. Install build dependencies (Common for both Rust and C)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    jq \
    libpq-dev \
    pkg-config \
    postgresql-server-dev-17

# 2. Install Rust (Needed for pgvectorscale)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# 3. Build pgvectorscale (Rust-based)
WORKDIR /tmp
RUN git clone --branch 0.9.0 https://github.com/timescale/pgvectorscale
WORKDIR /tmp/pgvectorscale/pgvectorscale

# Install cargo-pgrx with matching version
RUN cargo install --locked cargo-pgrx --version $(cargo metadata --format-version 1 | jq -r '.packages[] | select(.name == "pgrx") | .version')

# Initialize pgrx and install
RUN cargo pgrx init --pg17 $(which pg_config)
RUN cargo pgrx install --release

# 4. Build pg_textsearch (C-based/Make)
WORKDIR /tmp
RUN git clone --branch v1.0.0 https://github.com/timescale/pg_textsearch
WORKDIR /tmp/pg_textsearch
RUN make
RUN make install

# ==========================================
# Stage 2: Final Runtime
# ==========================================
FROM pgvector/pgvector:pg17

# Copy all library files (.so) from the builder
# This overwrites existing standard libs with identical copies but ensures
# we catch vectorscale.so, pg_textsearch.so, and any others.
COPY --from=builder /usr/lib/postgresql/17/lib/ /usr/lib/postgresql/17/lib/

# Copy all extension metadata (.control, .sql)
COPY --from=builder /usr/share/postgresql/17/extension/ /usr/share/postgresql/17/extension/

# pg_textsearch must be preloaded before CREATE EXTENSION (see upstream README).
RUN echo "shared_preload_libraries = 'pg_textsearch'" >> /usr/share/postgresql/17/postgresql.conf.sample

COPY ./init-database.sh /docker-entrypoint-initdb.d/init-database.sh
