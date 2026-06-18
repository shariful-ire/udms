"use client";

import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  BarChart, Bar,
} from "recharts";
import { EXPENSE_CATEGORY_COLORS } from "@/lib/constants";
import { formatCurrency, formatDate } from "@/lib/utils";
import { EmptyState } from "@/components/shared/LoadingSpinner";
import { PieChartIcon } from "lucide-react";

// ── Shared tooltip styles ─────────────────────────────────────────────────────
const tooltipStyle = {
  contentStyle: {
    backgroundColor: "hsl(var(--card))",
    border: "1px solid hsl(var(--border))",
    borderRadius: "0.5rem",
    fontSize: "0.8125rem",
    color: "hsl(var(--foreground))",
    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
  },
  itemStyle: { color: "hsl(var(--foreground))" },
  labelStyle: { color: "hsl(var(--muted-foreground))", fontWeight: 600 },
};

// ── ExpensePieChart ───────────────────────────────────────────────────────────
export function ExpensePieChart({ data = [] }) {
  if (!data.length) {
    return <EmptyState icon={PieChartIcon} title="No expense data" description="Expenses will appear here once recorded." />;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={65}
          outerRadius={100}
          paddingAngle={2}
          dataKey="amount"
          nameKey="category"
        >
          {data.map((entry, i) => (
            <Cell
              key={entry.category}
              fill={EXPENSE_CATEGORY_COLORS[entry.category] ?? `hsl(${i * 45}, 60%, 55%)`}
              strokeWidth={0}
            />
          ))}
        </Pie>
        <Tooltip
          {...tooltipStyle}
          formatter={(val) => [formatCurrency(val), "Amount"]}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(val) => val.replace(/_/g, " ")}
          wrapperStyle={{ fontSize: "0.75rem", paddingTop: "16px" }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

// ── MealTrendChart ────────────────────────────────────────────────────────────
export function MealTrendChart({ data = [] }) {
  const COLORS = {
    breakfast: "#f59e0b",
    lunch: "#3b82f6",
    dinner: "#8b5cf6",
    total: "#22c55e",
  };

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => {
            try { return new Date(v).toLocaleDateString("en", { month: "short", day: "numeric" }); }
            catch { return v; }
          }}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
          allowDecimals={false}
        />
        <Tooltip
          {...tooltipStyle}
          labelFormatter={(v) => formatDate(v)}
        />
        <Legend
          wrapperStyle={{ fontSize: "0.75rem", paddingTop: "16px" }}
          iconType="circle"
          iconSize={8}
        />
        {["breakfast", "lunch", "dinner"].map((key) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            name={key.charAt(0).toUpperCase() + key.slice(1)}
            stroke={COLORS[key]}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

// ── IncomeExpenseChart ────────────────────────────────────────────────────────
export function IncomeExpenseChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }} barCategoryGap="35%">
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
        <XAxis
          dataKey="period"
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          tickLine={false}
          axisLine={false}
          tickFormatter={(v) => formatCurrency(v, { compact: true, decimals: 0 })}
        />
        <Tooltip
          {...tooltipStyle}
          formatter={(val) => formatCurrency(val)}
        />
        <Legend
          wrapperStyle={{ fontSize: "0.75rem", paddingTop: "16px" }}
          iconType="square"
          iconSize={10}
        />
        <Bar dataKey="income" name="Income" fill="#22c55e" radius={[4, 4, 0, 0]} />
        <Bar dataKey="expense" name="Expense" fill="#f87171" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
