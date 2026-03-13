import React from "react";
import {
  DndContext,
  DragOverlay,
  type DragEndEvent,
  type DragStartEvent,
  PointerSensor,
  useDroppable,
  useSensor,
  useSensors,
  closestCenter,
} from "@dnd-kit/core";
import { SortableContext, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { JobCard } from "./JobCard";

type Job = {
  id: string;
  company: string;
  title: string;
  location?: string;
  url?: string;
  posted_at?: string | null;
  provider?: string;
  state?: string | null;
  ai_relevance_score?: number | null;
  raw_provider_payload_json?: string | null;
};

type SavedJobsBoardProps = {
  jobsByState: Record<string, Job[]>;
  selectedJob: Job | null;
  onSelectJob: (job: Job) => void;
  toggleJobPriority: (jobId: string, currentState?: string | null) => void;
  updateUserJobState: (jobId: string, newState: string) => void;
  showHeader?: boolean;
};

const PIPELINE_STATES = ["saved", "applied", "interview", "offer"] as const;

function SortableJobCard({
  job,
  selected,
  onSelectJob,
  toggleJobPriority,
  updateUserJobState,
}: {
  job: Job;
  selected: boolean;
  onSelectJob: (job: Job) => void;
  toggleJobPriority: (jobId: string, currentState?: string | null) => void;
  updateUserJobState: (jobId: string, newState: string) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: job.id,
  });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition: "none",
    opacity: isDragging ? 0.7 : 1,
    touchAction: "none",
    width: "100%",
  };

  return (
    <div ref={setNodeRef} style={{ ...style, position: "relative" }} {...attributes} {...listeners}>
      <JobCard
        job={job}
        selected={selected}
        onClick={() => onSelectJob(job)}
        onSave={() => toggleJobPriority(job.id, job.state)}
        onStatusChange={(newStatus) => updateUserJobState(job.id, newStatus)}
        variant="board"
      />
    </div>
  );
}

function DropColumn({ state, children }: { state: string; children: React.ReactNode }) {
  const { setNodeRef, isOver } = useDroppable({ id: state });

  return (
    <div
      ref={setNodeRef}
      style={{
        background: isOver ? "#f0f7ff" : "#fafafa",
        borderRadius: "10px",
        padding: "14px",
        minHeight: "140px",
        boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
      }}
    >
      {children}
    </div>
  );
}

export function SavedJobsBoard({
  jobsByState,
  selectedJob,
  onSelectJob,
  toggleJobPriority,
  updateUserJobState,
  showHeader = true,
}: SavedJobsBoardProps) {
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    })
  );
  const [activeJob, setActiveJob] = React.useState<Job | null>(null);

  const allJobs = PIPELINE_STATES.flatMap((state) => jobsByState[state] ?? []);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    const jobId = String(active.id);
    const dragged = allJobs.find((job) => job.id === jobId);
    if (!dragged) return;

    const overId = String(over.id);
    let newState = overId;

    if (!PIPELINE_STATES.includes(overId as (typeof PIPELINE_STATES)[number])) {
      const overJob = allJobs.find((job) => job.id === overId);
      if (!overJob || !overJob.state) return;
      newState = overJob.state;
    }

    if (dragged.state === newState) return;
    updateUserJobState(jobId, newState);
  };

  const handleDragStart = (event: DragStartEvent) => {
    const jobId = String(event.active.id);
    const dragged = allJobs.find((job) => job.id === jobId) ?? null;
    setActiveJob(dragged);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={(event) => {
        handleDragEnd(event);
        setActiveJob(null);
      }}
      onDragCancel={() => setActiveJob(null)}
    >
      {showHeader && (
        <div style={{ marginBottom: "24px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "16px" }}>
            <h1 style={{ margin: 0, fontSize: "24px", color: "#111827" }}>Saved Jobs Pipeline</h1>
          </div>
          <p style={{ margin: "8px 0 0 0", color: "#666", fontSize: "13px" }}>
            Drag jobs between columns to move them through your application process.
          </p>
        </div>
      )}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: "24px",
        }}
      >
        {PIPELINE_STATES.map((state) => {
          const columnJobs = jobsByState[state] ?? [];
          return (
            <div key={state} style={{ minWidth: 0 }}>
              <h4
                style={{
                  marginBottom: "12px",
                  textTransform: "capitalize",
                  fontSize: "16px",
                  fontWeight: 700,
                  color: "#111827",
                  letterSpacing: "0.01em",
                }}
              >
                {state}
              </h4>
              <DropColumn state={state}>
                <SortableContext items={columnJobs.map((job) => job.id)} strategy={verticalListSortingStrategy}>
                  <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                    {columnJobs.map((job) => (
                      <SortableJobCard
                        key={job.id}
                        job={job}
                        selected={selectedJob?.id === job.id}
                        onSelectJob={onSelectJob}
                        toggleJobPriority={toggleJobPriority}
                        updateUserJobState={updateUserJobState}
                      />
                    ))}
                  </div>
                </SortableContext>
              </DropColumn>
            </div>
          );
        })}
      </div>
      <DragOverlay dropAnimation={null}>
        {activeJob ? (
          <div style={{ width: "280px" }}>
            <JobCard
              job={activeJob}
              selected={false}
              onClick={() => {}}
              onSave={() => {}}
              isDragging
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
