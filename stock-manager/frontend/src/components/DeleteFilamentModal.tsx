import { Filament } from "../api";
import ConfirmDeleteModal from "./ConfirmDeleteModal";

interface Props {
  filament: Filament;
  onCancel: () => void;
  onConfirm: () => void;
  confirming?: boolean;
}

export default function DeleteFilamentModal({ filament, onCancel, onConfirm, confirming }: Props) {
  return (
    <ConfirmDeleteModal
      title="Delete filament?"
      warning="All colors and stock history for this filament will be removed permanently. This cannot be undone."
      onCancel={onCancel}
      onConfirm={onConfirm}
      confirming={confirming}
    >
      <p style={{ margin: 0 }}>
        Are you sure you want to delete{" "}
        <strong>
          {filament.brand} {filament.material}
        </strong>{" "}
        ({filament.filament_type})?
      </p>
    </ConfirmDeleteModal>
  );
}
