"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { authClient } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Loader2, Chrome, Github, ArrowRight, Building2, CheckCircle2, Briefcase } from "lucide-react";

export default function SignupPage() {
  const router = useRouter();

  const [step, setStep] = useState<"signup" | "onboarding">("signup");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [investmentFocus, setInvestmentFocus] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isGithubLoading, setIsGithubLoading] = useState(false);
  const [error, setError] = useState("");

  const validatePassword = (pass: string) => {
    if (pass.length < 8) return "Password must be at least 8 characters";
    if (!/[A-Z]/.test(pass)) return "Password must contain an uppercase letter";
    if (!/[a-z]/.test(pass)) return "Password must contain a lowercase letter";
    if (!/[0-9]/.test(pass)) return "Password must contain a number";
    return null;
  };

  const handleEmailSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate password
    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);

    try {
      const { data, error } = await authClient.signUp.email({
        email,
        password,
        name,
        callbackURL: "/dashboard",
      });

      if (error) {
        setError(error.message || "Failed to create account");
        setIsLoading(false);
        return;
      }

      if (data) {
        setStep("onboarding");
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
      setIsLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setError("");
    setIsGoogleLoading(true);

    try {
      await authClient.signIn.social({
        provider: "google",
        callbackURL: "/dashboard",
      });
    } catch (err) {
      setError("Failed to sign up with Google. Please try again.");
      setIsGoogleLoading(false);
    }
  };

  const handleGithubSignup = async () => {
    setError("");
    setIsGithubLoading(true);

    try {
      await authClient.signIn.social({
        provider: "github",
        callbackURL: "/dashboard",
      });
    } catch (err) {
      setError("Failed to sign up with GitHub. Please try again.");
      setIsGithubLoading(false);
    }
  };

  const handleOnboardingComplete = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Here you would typically save the onboarding data
    // For now, we'll just redirect to the dashboard
    await new Promise((resolve) => setTimeout(resolve, 500));

    router.push("/dashboard");
    router.refresh();
  };

  if (step === "onboarding") {
    return (
      <div className="animate-fade-in">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#C9A227] to-[#D4B43D] flex items-center justify-center shadow-lg shadow-[#C9A227]/20 group-hover:shadow-[#C9A227]/30 transition-all duration-300">
              <Building2 className="w-6 h-6 text-[#0A1628]" />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight">
              ACQUISITOR
            </span>
          </Link>
        </div>

        <Card className="border-[#1E3160] bg-[#0F1D32]/90 backdrop-blur-sm shadow-2xl">
          <CardHeader className="space-y-1 pb-6">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-full bg-[#C9A227]/20 flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-[#C9A227]" />
              </div>
            </div>
            <CardTitle className="text-2xl font-semibold text-white text-center">
              Account created!
            </CardTitle>
            <CardDescription className="text-center text-[#8BA4D1]">
              Tell us a bit more about yourself to personalize your experience
            </CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleOnboardingComplete} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="companyName" className="text-sm font-medium text-[#DEE6F3]">
                  Company Name (Optional)
                </Label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#5B7BB8]" />
                  <Input
                    id="companyName"
                    placeholder="Your company or firm name"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="h-12 pl-10 bg-[#162544] border-[#1E3160] text-white placeholder:text-[#5B7BB8] focus:border-[#C9A227] focus:ring-[#C9A227]/20"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label className="text-sm font-medium text-[#DEE6F3]">
                  Investment Focus (Optional)
                </Label>
                <div className="grid grid-cols-2 gap-3">
                  {["SaaS", "E-commerce", "Manufacturing", "Services", "Healthcare", "Other"].map((focus) => (
                    <button
                      key={focus}
                      type="button"
                      onClick={() => setInvestmentFocus(focus)}
                      className={`px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        investmentFocus === focus
                          ? "bg-[#C9A227] text-[#0A1628]"
                          : "bg-[#162544] border border-[#1E3160] text-[#DEE6F3] hover:border-[#3B5A9A] hover:bg-[#1E3160]"
                      }`}
                    >
                      {focus}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-12 bg-gradient-to-r from-[#C9A227] to-[#D4B43D] hover:from-[#D4B43D] hover:to-[#E0C85A] text-[#0A1628] font-semibold shadow-lg shadow-[#C9A227]/20 hover:shadow-[#C9A227]/30 transition-all duration-300"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Setting up...
                  </>
                ) : (
                  <>
                    Complete Setup
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </>
                )}
              </Button>

              <Button
                type="button"
                variant="ghost"
                className="w-full h-11 text-[#8BA4D1] hover:text-white hover:bg-[#162544]"
                onClick={() => {
                  router.push("/dashboard");
                  router.refresh();
                }}
              >
                Skip for now
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Logo */}
      <div className="flex justify-center mb-8">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#C9A227] to-[#D4B43D] flex items-center justify-center shadow-lg shadow-[#C9A227]/20 group-hover:shadow-[#C9A227]/30 transition-all duration-300">
            <Building2 className="w-6 h-6 text-[#0A1628]" />
          </div>
          <span className="text-2xl font-bold text-white tracking-tight">
            ACQUISITOR
          </span>
        </Link>
      </div>

      <Card className="border-[#1E3160] bg-[#0F1D32]/90 backdrop-blur-sm shadow-2xl">
        <CardHeader className="space-y-1 pb-6">
          <CardTitle className="text-2xl font-semibold text-white text-center">
            Create your account
          </CardTitle>
          <CardDescription className="text-center text-[#8BA4D1]">
            Start your journey to finding the perfect acquisition
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Social Signup Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              variant="outline"
              className="h-11 border-[#1E3160] bg-transparent hover:bg-[#162544] hover:border-[#3B5A9A] text-white"
              onClick={handleGoogleSignup}
              disabled={isGoogleLoading || isLoading}
            >
              {isGoogleLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Chrome className="mr-2 h-4 w-4 text-[#C9A227]" />
              )}
              Google
            </Button>
            <Button
              variant="outline"
              className="h-11 border-[#1E3160] bg-transparent hover:bg-[#162544] hover:border-[#3B5A9A] text-white"
              onClick={handleGithubSignup}
              disabled={isGithubLoading || isLoading}
            >
              {isGithubLoading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Github className="mr-2 h-4 w-4 text-[#C9A227]" />
              )}
              GitHub
            </Button>
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[#1E3160]" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-[#0F1D32] px-3 text-[#5B7BB8]">
                Or continue with email
              </span>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Signup Form */}
          <form onSubmit={handleEmailSignup} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-sm font-medium text-[#DEE6F3]">
                Full Name
              </Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-[#162544] border-[#1E3160] text-white placeholder:text-[#5B7BB8] focus:border-[#C9A227] focus:ring-[#C9A227]/20"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-[#DEE6F3]">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-[#162544] border-[#1E3160] text-white placeholder:text-[#5B7BB8] focus:border-[#C9A227] focus:ring-[#C9A227]/20"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-[#DEE6F3]">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Create a strong password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-[#162544] border-[#1E3160] text-white placeholder:text-[#5B7BB8] focus:border-[#C9A227] focus:ring-[#C9A227]/20"
                required
              />
              <p className="text-xs text-[#5B7BB8]">
                Must be at least 8 characters with uppercase, lowercase, and number
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium text-[#DEE6F3]">
                Confirm Password
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
                className="h-12 bg-[#162544] border-[#1E3160] text-white placeholder:text-[#5B7BB8] focus:border-[#C9A227] focus:ring-[#C9A227]/20"
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full h-12 bg-gradient-to-r from-[#C9A227] to-[#D4B43D] hover:from-[#D4B43D] hover:to-[#E0C85A] text-[#0A1628] font-semibold shadow-lg shadow-[#C9A227]/20 hover:shadow-[#C9A227]/30 transition-all duration-300"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating account...
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </Button>
          </form>
        </CardContent>

        <CardFooter className="flex flex-col space-y-4 pt-2">
          <div className="text-center text-sm text-[#8BA4D1]">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-[#C9A227] hover:text-[#D4B43D] transition-colors"
            >
              Sign in
            </Link>
          </div>

          <p className="text-center text-xs text-[#5B7BB8]">
            By creating an account, you agree to our{" "}
            <Link href="#" className="text-[#8BA4D1] hover:text-[#C9A227]">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="#" className="text-[#8BA4D1] hover:text-[#C9A227]">
              Privacy Policy
            </Link>
          </p>
        </CardFooter>
      </Card>

      {/* Footer */}
      <p className="mt-8 text-center text-xs text-[#5B7BB8]">
        Protected by industry-standard encryption
      </p>
    </div>
  );
}
