"use client";

import { Component } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

/**
 * ErrorBoundary
 *
 * Catches JavaScript errors in child component trees and shows a fallback UI
 * instead of crashing the whole application.
 *
 * Usage:
 *   <ErrorBoundary>
 *     <SomeDangerousComponent />
 *   </ErrorBoundary>
 */
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    // Log to error tracking service in production
    if (process.env.NODE_ENV !== "production") {
      console.error("[ErrorBoundary]", error, info.componentStack);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex flex-col items-center justify-center gap-4 rounded-xl border border-destructive/20 bg-destructive/5 px-6 py-12 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10">
            <AlertTriangle className="h-6 w-6 text-destructive" />
          </div>

          <div className="space-y-1">
            <h3 className="font-semibold text-foreground">Something went wrong</h3>
            <p className="max-w-sm text-sm text-muted-foreground">
              {this.props.message ??
                "An unexpected error occurred. Please try refreshing."}
            </p>
            {process.env.NODE_ENV !== "production" && this.state.error && (
              <pre className="mt-2 max-w-sm overflow-auto rounded bg-muted px-3 py-2 text-left text-xs text-muted-foreground">
                {this.state.error.message}
              </pre>
            )}
          </div>

          <button
            onClick={this.handleReset}
            className="flex items-center gap-2 rounded-lg bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/20 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
