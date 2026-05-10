"use client";

import { Component, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error) {
    console.error("UI Error:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="flex flex-col items-center justify-center h-screen gap-4">
            <div className="text-4xl">😵</div>
            <p className="text-lg font-semibold text-foreground">
              Terjadi kesalahan
            </p>
            <p className="text-sm text-muted-foreground max-w-md text-center">
              Aplikasi mengalami error yang tidak terduga. Silakan coba lagi.
            </p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="px-6 py-2.5 bg-foreground text-background rounded-lg text-sm font-medium hover:bg-foreground/90 transition-smooth"
            >
              Coba Lagi
            </button>
          </div>
        )
      );
    }
    return this.props.children;
  }
}
