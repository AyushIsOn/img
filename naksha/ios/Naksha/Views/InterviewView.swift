import SwiftUI

/// The intake conversation, one question at a time.
///
/// Deliberately not a chat transcript. A chat bubble list makes the user scroll
/// back through their own answers and invites free text where a number is
/// wanted. Instead each question owns the screen and brings the right control
/// with it, so a count is a stepper and a set of options is a row of chips.
/// The questions are written by a model; the controls are not.
struct InterviewView: View {
    @EnvironmentObject private var store: DesignStore

    @State private var text = ""
    @State private var number: Double = 5
    @State private var count = 1
    @State private var picked: Set<String> = []

    var body: some View {
        interview
        .task {
            if store.question == nil && !store.interviewDone {
                await store.advanceInterview()
            }
        }
    }

    // MARK: Question flow

    private var interview: some View {
        VStack(alignment: .leading, spacing: 0) {
            header

            Spacer(minLength: 12)

            if let question = store.question {
                VStack(alignment: .leading, spacing: 22) {
                    Text(question.prompt)
                        .font(.system(size: 30, weight: .bold))
                        .foregroundStyle(Theme.ink)
                        .fixedSize(horizontal: false, vertical: true)

                    if let helper = question.helper, !helper.isEmpty {
                        Text(helper)
                            .font(.subheadline)
                            .foregroundStyle(Theme.muted)
                            .fixedSize(horizontal: false, vertical: true)
                    }

                    control(for: question)
                }
                .padding(24)
                .frame(maxWidth: .infinity, alignment: .leading)
                .glassCard(28)
                .padding(.horizontal, 18)
                // A fresh identity per question so each one animates in
                // rather than the text swapping in place.
                .id(question.id)
                .transition(.asymmetric(
                    insertion: .move(edge: .trailing).combined(with: .opacity),
                    removal: .move(edge: .leading).combined(with: .opacity)))
            } else if store.interviewBusy {
                thinking
            } else if let problem = store.interviewError {
                failure(problem)
            }

            Spacer(minLength: 12)

            if let question = store.question {
                continueButton(for: question)
            }
        }
        .animation(.spring(response: 0.5, dampingFraction: 0.85),
                   value: store.question?.id)
    }

    private var header: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(alignment: .center) {
                BrandText(text: "NAKSHA", size: 26)
                Spacer()
                sourceBadge
            }
            Text("A few questions, then we design your wiring.")
                .font(.footnote)
                .foregroundStyle(Theme.muted)
            progress
        }
        .padding(.horizontal, 24)
        .padding(.top, 18)
    }

    /// States plainly whether the model is writing the questions. Claiming an
    /// interview is AI driven while the script is running would be the easiest
    /// thing in the world to get caught doing.
    private var sourceBadge: some View {
        HStack(spacing: 5) {
            Image(systemName: store.interviewSource == "llm"
                  ? "sparkles" : "list.bullet.rectangle")
                .font(.system(size: 10, weight: .bold))
            Text(store.interviewSource == "llm" ? "AI interview"
                                                : "Standard questions")
                .font(.system(size: 10, weight: .semibold))
        }
        .foregroundStyle(store.interviewSource == "llm"
                         ? Brand.gold : Theme.muted)
        .padding(.vertical, 6)
        .padding(.horizontal, 11)
        .glassChip(tint: store.interviewSource == "llm" ? Brand.amber : nil)
    }

    private var progress: some View {
        let asked = store.answers.count
        let estimate = max(8, asked + 1)
        return HStack(spacing: 5) {
            ForEach(0..<estimate, id: \.self) { i in
                Capsule()
                    .fill(i < asked ? AnyShapeStyle(Brand.markGradient)
                                    : AnyShapeStyle(Color.white.opacity(0.16)))
                    .frame(height: 4)
            }
        }
        .animation(.easeOut(duration: 0.3), value: asked)
    }

    private var thinking: some View {
        HStack(spacing: 12) {
            ProgressView().tint(Brand.amber)
            Text(store.answers.isEmpty ? "Starting up"
                                       : "Thinking about your answer")
                .font(.subheadline)
                .foregroundStyle(Theme.muted)
        }
        .padding(22)
        .glassCard(22)
        .padding(.horizontal, 18)
    }

    /// Also the offline escape hatch.
    ///
    /// The interview needs the solver, so a network problem lands the user on
    /// the very first screen with nowhere to go. The bundled sample is real
    /// solver output, so every screen after this one still works from it and
    /// there is always something to show.
    private func failure(_ message: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Label("Cannot reach the solver", systemImage:
                    "antenna.radiowaves.left.and.right.slash")
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(Theme.warn)
            Text(message)
                .font(.caption)
                .foregroundStyle(Theme.muted)
                .fixedSize(horizontal: false, vertical: true)

            Button("Try again") { Task { await store.advanceInterview() } }
                .buttonStyle(.vguardGlass)

            Divider().overlay(Brand.hairline)

            if let design = store.design {
                NavigationLink { DesignTabsView(design: design) } label: {
                    Label("Open the sample drawings",
                          systemImage: "doc.richtext")
                }
                .buttonStyle(.vguard)
            } else {
                Button {
                    store.loadSample()
                } label: {
                    Label("Work offline from the sample",
                          systemImage: "arrow.down.doc")
                }
                .buttonStyle(.vguardGlass)
                Text("A finished 2 BHK from the design engine. Drawing, "
                     + "circuits, AR and the material list all work from it "
                     + "with no laptop on the network.")
                    .font(.caption2)
                    .foregroundStyle(Theme.muted)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .padding(20)
        .glassCard(22)
        .padding(.horizontal, 18)
    }

    // MARK: Controls

    @ViewBuilder
    private func control(for question: InterviewQuestion) -> some View {
        switch question.kind {
        case .text:
            TextField("", text: $text, prompt: Text("Type your answer")
                .foregroundColor(Theme.muted))
                .textInputAutocapitalization(.words)
                .font(.title3.weight(.semibold))
                .foregroundStyle(Theme.ink)
                .padding(.vertical, 14)
                .padding(.horizontal, 16)
                .glassChip()

        case .number:
            HStack(spacing: 14) {
                Text(String(format: "%g", number))
                    .font(Brand.display(38))
                    .foregroundStyle(Brand.markGradient)
                if let unit = question.unit {
                    Text(unit).font(.title3.weight(.semibold))
                        .foregroundStyle(Theme.muted)
                }
                Spacer()
            }
            Slider(value: $number,
                   in: (question.min ?? 1)...(question.max ?? 20),
                   step: 0.5)

        case .count:
            HStack(spacing: 18) {
                stepButton("minus") {
                    count = max(Int(question.min ?? 0), count - 1)
                }
                Text("\(count)")
                    .font(Brand.display(40))
                    .foregroundStyle(Brand.markGradient)
                    .frame(minWidth: 62)
                    .contentTransition(.numericText())
                stepButton("plus") {
                    count = min(Int(question.max ?? 12), count + 1)
                }
                Spacer()
            }
            .animation(.spring(response: 0.3, dampingFraction: 0.7),
                       value: count)

        case .choice, .multi:
            let options = question.options ?? []
            FlowChips(options: options,
                      selected: picked,
                      multiple: question.kind == .multi) { option in
                if question.kind == .multi {
                    if picked.contains(option) { picked.remove(option) }
                    else { picked.insert(option) }
                } else {
                    picked = [option]
                }
            }
        }
    }

    private func stepButton(_ symbol: String,
                            action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: symbol)
                .font(.system(size: 17, weight: .bold))
                .foregroundStyle(Theme.ink)
                .frame(width: 48, height: 48)
                .glassChip()
        }
        .buttonStyle(.plain)
    }

    // MARK: Submit

    private func continueButton(for question: InterviewQuestion) -> some View {
        Button {
            Task { await submit(question) }
        } label: {
            Label(store.answers.isEmpty ? "Start" : "Continue",
                  systemImage: "arrow.right")
        }
        .buttonStyle(.vguard)
        .disabled(!isAnswerable(question) || store.interviewBusy)
        .opacity(isAnswerable(question) ? 1 : 0.45)
        .padding(.horizontal, 18)
        .padding(.bottom, 22)
    }

    private func isAnswerable(_ question: InterviewQuestion) -> Bool {
        switch question.kind {
        case .text: return !text.trimmingCharacters(in: .whitespaces).isEmpty
        case .choice, .multi: return !picked.isEmpty
        case .number, .count: return true
        }
    }

    private func submit(_ question: InterviewQuestion) async {
        let value: AnswerValue
        switch question.kind {
        case .text:   value = .text(text.trimmingCharacters(in: .whitespaces))
        case .number: value = .text(String(format: "%g", number))
        case .count:  value = .text("\(count)")
        case .choice, .multi: value = .list(Array(picked).sorted())
        }
        // Reset the controls before the next question arrives so the incoming
        // card never briefly shows the previous answer.
        text = ""
        number = question.unit == "kW" ? 5 : 1
        count = 1
        picked = []
        await store.answer(value)
    }
}

// MARK: - Chips that wrap

/// A wrapping row of options. `Layout` rather than a `LazyVGrid` because the
/// options are short and unevenly sized, and a grid would leave ragged gaps.
private struct FlowChips: View {
    let options: [String]
    let selected: Set<String>
    let multiple: Bool
    let tap: (String) -> Void

    var body: some View {
        FlowLayout(spacing: 9) {
            ForEach(options, id: \.self) { option in
                let on = selected.contains(option)
                Button { tap(option) } label: {
                    HStack(spacing: 6) {
                        if multiple {
                            Image(systemName: on ? "checkmark.circle.fill"
                                                 : "circle")
                                .font(.system(size: 12, weight: .semibold))
                        }
                        Text(option).font(.subheadline.weight(.medium))
                    }
                    .foregroundStyle(on ? Color.black : Theme.ink)
                    .padding(.vertical, 11)
                    .padding(.horizontal, 15)
                    .background(on ? AnyShapeStyle(Brand.markGradient)
                                   : AnyShapeStyle(Color.clear),
                                in: .capsule)
                    .glassChip(tint: on ? Brand.amber : nil)
                }
                .buttonStyle(.plain)
            }
        }
        .animation(.spring(response: 0.3, dampingFraction: 0.75),
                   value: selected)
    }
}

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize,
                      subviews: Subviews,
                      cache: inout ()) -> CGSize {
        let width = proposal.width ?? 320
        var x: CGFloat = 0, y: CGFloat = 0, lineHeight: CGFloat = 0
        for view in subviews {
            let size = view.sizeThatFits(.unspecified)
            if x + size.width > width, x > 0 {
                x = 0
                y += lineHeight + spacing
                lineHeight = 0
            }
            x += size.width + spacing
            lineHeight = max(lineHeight, size.height)
        }
        return CGSize(width: width, height: y + lineHeight)
    }

    func placeSubviews(in bounds: CGRect,
                       proposal: ProposedViewSize,
                       subviews: Subviews,
                       cache: inout ()) {
        var x = bounds.minX, y = bounds.minY, lineHeight: CGFloat = 0
        for view in subviews {
            let size = view.sizeThatFits(.unspecified)
            if x + size.width > bounds.maxX, x > bounds.minX {
                x = bounds.minX
                y += lineHeight + spacing
                lineHeight = 0
            }
            view.place(at: CGPoint(x: x, y: y), proposal: .unspecified)
            x += size.width + spacing
            lineHeight = max(lineHeight, size.height)
        }
    }
}
